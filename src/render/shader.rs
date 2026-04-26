use web_sys::{WebGl2RenderingContext as GL, WebGlProgram, WebGlShader};
use std::collections::HashMap;

pub struct ShaderProgram {
    pub program: WebGlProgram,
    pub uniforms: HashMap<String, web_sys::WebGlUniformLocation>,
}

impl ShaderProgram {
    pub fn compile(gl: &GL, vert_src: &str, frag_src: &str) -> Result<Self, String> {
        let vert = compile_shader(gl, GL::VERTEX_SHADER, vert_src)?;
        let frag = compile_shader(gl, GL::FRAGMENT_SHADER, frag_src)?;

        let program: WebGlProgram = gl.create_program().ok_or("Failed to create program")?;
        gl.attach_shader(&program, &vert);
        gl.attach_shader(&program, &frag);
        gl.link_program(&program);

        if !gl.get_program_parameter(&program, GL::LINK_STATUS).as_bool().unwrap_or(false) {
            let info = gl.get_program_info_log(&program).unwrap_or_default();
            gl.delete_program(Some(&program));
            return Err(format!("Shader link failed: {}", info));
        }

        gl.delete_shader(Some(&vert));
        gl.delete_shader(Some(&frag));

        Ok(Self {
            program,
            uniforms: HashMap::new(),
        })
    }

    pub fn cache_uniform(&mut self, gl: &GL, name: &str) {
        let loc = gl.get_uniform_location(&self.program, name);
        if let Some(loc) = loc {
            self.uniforms.insert(name.to_string(), loc);
        }
    }

    pub fn uniform_1f(&self, gl: &GL, name: &str, v: f32) {
        if let Some(loc) = self.uniforms.get(name) {
            gl.uniform1f(Some(loc), v);
        }
    }

    pub fn uniform_2f(&self, gl: &GL, name: &str, x: f32, y: f32) {
        if let Some(loc) = self.uniforms.get(name) {
            gl.uniform2f(Some(loc), x, y);
        }
    }

    pub fn uniform_3f(&self, gl: &GL, name: &str, x: f32, y: f32, z: f32) {
        if let Some(loc) = self.uniforms.get(name) {
            gl.uniform3f(Some(loc), x, y, z);
        }
    }

    pub fn uniform_4f(&self, gl: &GL, name: &str, x: f32, y: f32, z: f32, w: f32) {
        if let Some(loc) = self.uniforms.get(name) {
            gl.uniform4f(Some(loc), x, y, z, w);
        }
    }

    pub fn uniform_matrix3fv(&self, gl: &GL, name: &str, mat: &[f32; 9]) {
        if let Some(loc) = self.uniforms.get(name) {
            gl.uniform_matrix3fv_with_f32_array(Some(loc), false, mat);
        }
    }

    pub fn uniform_matrix4fv(&self, gl: &GL, name: &str, mat: &[f32; 16]) {
        if let Some(loc) = self.uniforms.get(name) {
            gl.uniform_matrix4fv_with_f32_array(Some(loc), false, mat);
        }
    }

    pub fn uniform_1i(&self, gl: &GL, name: &str, v: i32) {
        if let Some(loc) = self.uniforms.get(name) {
            gl.uniform1i(Some(loc), v);
        }
    }

    pub fn bind(&self, gl: &GL) {
        gl.use_program(Some(&self.program));
    }
}

fn compile_shader(gl: &GL, shader_type: u32, source: &str) -> Result<WebGlShader, String> {
    let shader: WebGlShader = gl.create_shader(shader_type).ok_or("Failed to create shader")?;
    gl.shader_source(&shader, source);
    gl.compile_shader(&shader);

    if !gl.get_shader_parameter(&shader, GL::COMPILE_STATUS).as_bool().unwrap_or(false) {
        let info = gl.get_shader_info_log(&shader).unwrap_or_default();
        gl.delete_shader(Some(&shader));
        return Err(format!("Shader compile failed: {}", info));
    }

    Ok(shader)
}
