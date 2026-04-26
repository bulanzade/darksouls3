use crate::render::shader::ShaderProgram;
use web_sys::WebGl2RenderingContext as GL;

pub struct Light {
    pub x: f32,
    pub y: f32,
    pub radius: f32,
    pub color: [f32; 3],
    pub intensity: f32,
}

pub struct LightRenderer {
    shader: ShaderProgram,
    vao: web_sys::WebGlVertexArrayObject,
    #[allow(dead_code)]
    vbo: web_sys::WebGlBuffer,
}

impl LightRenderer {
    pub fn new(gl: &GL) -> Result<Self, String> {
        let vert_src = include_str!("../../static/shaders/light.vert");
        let frag_src = include_str!("../../static/shaders/light.frag");
        let mut shader = ShaderProgram::compile(gl, vert_src, frag_src)?;
        shader.cache_uniform(gl, "u_projection");
        shader.cache_uniform(gl, "u_light_pos");
        shader.cache_uniform(gl, "u_light_color");
        shader.cache_uniform(gl, "u_light_radius");
        shader.cache_uniform(gl, "u_light_intensity");
        shader.cache_uniform(gl, "u_screen_size");

        let vao: web_sys::WebGlVertexArrayObject =
            gl.create_vertex_array()
                .ok_or("Failed to create light VAO")?;
        gl.bind_vertex_array(Some(&vao));

        let vbo: web_sys::WebGlBuffer =
            gl.create_buffer().ok_or("Failed to create light VBO")?;
        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&vbo));

        // Fullscreen quad
        let verts: [f32; 8] = [-1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0];
        let verts_bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                verts.as_ptr() as *const u8,
                std::mem::size_of_val(&verts),
            )
        };
        gl.buffer_data_with_u8_array(GL::ARRAY_BUFFER, verts_bytes, GL::STATIC_DRAW);

        gl.enable_vertex_attrib_array(0);
        gl.vertex_attrib_pointer_with_i32(0, 2, GL::FLOAT, false, 8, 0);

        gl.bind_vertex_array(None);

        Ok(Self { shader, vao, vbo })
    }

    pub fn render_lights(
        &self,
        gl: &GL,
        lights: &[Light],
        projection: &[f32; 16],
        screen_w: f32,
        screen_h: f32,
    ) {
        self.shader.bind(gl);
        self.shader
            .uniform_matrix4fv(gl, "u_projection", projection);

        gl.bind_vertex_array(Some(&self.vao));

        gl.enable(GL::BLEND);
        gl.blend_func(GL::SRC_ALPHA, GL::ONE); // Additive blending for lights

        for light in lights.iter().take(8) {
            self.shader
                .uniform_2f(gl, "u_light_pos", light.x, light.y);
            self.shader.uniform_3f(
                gl,
                "u_light_color",
                light.color[0],
                light.color[1],
                light.color[2],
            );
            self.shader.uniform_1f(gl, "u_light_radius", light.radius);
            self.shader
                .uniform_1f(gl, "u_light_intensity", light.intensity);
            self.shader.uniform_2f(gl, "u_screen_size", screen_w, screen_h);

            gl.draw_arrays(GL::TRIANGLE_FAN, 0, 4);
        }

        gl.bind_vertex_array(None);
        gl.blend_func(GL::SRC_ALPHA, GL::ONE_MINUS_SRC_ALPHA); // Reset blend mode
    }
}
