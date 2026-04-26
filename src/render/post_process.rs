use crate::render::shader::ShaderProgram;
use web_sys::WebGl2RenderingContext as GL;

pub struct PostProcessor {
    shader: ShaderProgram,
    vao: web_sys::WebGlVertexArrayObject,
}

impl PostProcessor {
    pub fn new(gl: &GL) -> Result<Self, String> {
        let vert_src = include_str!("../../static/shaders/composite.vert");
        let frag_src = include_str!("../../static/shaders/composite.frag");
        let mut shader = ShaderProgram::compile(gl, vert_src, frag_src)?;
        shader.cache_uniform(gl, "u_scene");
        shader.cache_uniform(gl, "u_vignette_intensity");
        shader.cache_uniform(gl, "u_fog_color");
        shader.cache_uniform(gl, "u_fog_distance");
        shader.cache_uniform(gl, "u_brightness");
        shader.cache_uniform(gl, "u_saturation");

        let vao: web_sys::WebGlVertexArrayObject = gl
            .create_vertex_array()
            .ok_or("Failed to create composite VAO")?;
        gl.bind_vertex_array(Some(&vao));

        let vbo = gl
            .create_buffer()
            .ok_or("Failed to create composite VBO")?;
        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&vbo));
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

        Ok(Self { shader, vao })
    }

    pub fn render(
        &self,
        gl: &GL,
        vignette: f32,
        fog_color: [f32; 4],
        fog_distance: [f32; 2],
        brightness: f32,
        saturation: f32,
    ) {
        self.shader.bind(gl);
        self.shader.uniform_1i(gl, "u_scene", 0);
        self.shader
            .uniform_1f(gl, "u_vignette_intensity", vignette);
        self.shader.uniform_4f(
            gl,
            "u_fog_color",
            fog_color[0],
            fog_color[1],
            fog_color[2],
            fog_color[3],
        );
        self.shader
            .uniform_2f(gl, "u_fog_distance", fog_distance[0], fog_distance[1]);
        self.shader.uniform_1f(gl, "u_brightness", brightness);
        self.shader.uniform_1f(gl, "u_saturation", saturation);

        gl.bind_vertex_array(Some(&self.vao));
        gl.draw_arrays(GL::TRIANGLE_FAN, 0, 4);
        gl.bind_vertex_array(None);
    }
}
