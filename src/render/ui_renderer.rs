use web_sys::WebGl2RenderingContext as GL;

use crate::render::shader::ShaderProgram;
use crate::render::vertex::InstanceData;

pub struct UiRenderer {
    shader: ShaderProgram,
    vao: web_sys::WebGlVertexArrayObject,
    _quad_vbo: web_sys::WebGlBuffer,
    instance_vbo: web_sys::WebGlBuffer,
    white_tex: web_sys::WebGlTexture,
}

impl UiRenderer {
    pub fn new(gl: &GL) -> Result<Self, String> {
        // Re-use sprite shaders but with orthographic screen-space projection
        let vert_src = include_str!("../../static/shaders/sprite.vert");
        let frag_src = include_str!("../../static/shaders/sprite.frag");
        let mut shader = ShaderProgram::compile(gl, vert_src, frag_src)?;
        shader.cache_uniform(gl, "u_projection");
        shader.cache_uniform(gl, "u_texture");

        let vao: web_sys::WebGlVertexArrayObject =
            gl.create_vertex_array().ok_or("Failed to create UI VAO")?;
        gl.bind_vertex_array(Some(&vao));

        // Create a simple quad VBO for UI elements
        let quad_vbo = gl.create_buffer().ok_or("Failed to create UI VBO")?;
        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&quad_vbo));

        let verts: [f32; 16] = [
            -0.5, -0.5, 0.0, 0.0, 0.5, -0.5, 1.0, 0.0, 0.5, 0.5, 1.0, 1.0, -0.5, 0.5, 0.0, 1.0,
        ];
        let verts_bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                verts.as_ptr() as *const u8,
                std::mem::size_of_val(&verts),
            )
        };
        gl.buffer_data_with_u8_array(GL::ARRAY_BUFFER, verts_bytes, GL::STATIC_DRAW);

        let stride: i32 = 16; // 4 floats * 4 bytes
        // Location 0: a_pos (vec2)
        gl.enable_vertex_attrib_array(0);
        gl.vertex_attrib_pointer_with_i32(0, 2, GL::FLOAT, false, stride, 0);
        // Location 1: a_uv (vec2)
        gl.enable_vertex_attrib_array(1);
        gl.vertex_attrib_pointer_with_i32(1, 2, GL::FLOAT, false, stride, 8);

        // Instance VBO — same layout as SpriteBatcher
        let instance_vbo = gl
            .create_buffer()
            .ok_or("Failed to create UI instance VBO")?;
        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&instance_vbo));

        let instance_buf_size: i32 =
            crate::render::vertex::MAX_INSTANCES as i32 * std::mem::size_of::<InstanceData>() as i32;
        gl.buffer_data_with_i32(GL::ARRAY_BUFFER, instance_buf_size, GL::DYNAMIC_DRAW);

        let instance_stride = std::mem::size_of::<InstanceData>() as i32;

        // InstanceData layout:
        //   offset  0: transform [f32; 9] — 36 bytes
        //   offset 36: uv_rect   [f32; 4] — 16 bytes
        //   offset 52: color     [f32; 4] — 16 bytes
        //
        // Shader attribute locations:
        //   location 2: a_color     (vec4) at offset 52
        //   location 3: a_transform col0 (vec3) at offset 0
        //   location 4: a_transform col1 (vec3) at offset 12
        //   location 5: a_transform col2 (vec3) at offset 24
        //   location 6: a_uv_rect   (vec4) at offset 36

        let color_offset = (13 * std::mem::size_of::<f32>()) as i32; // 9 + 4 = 52
        gl.enable_vertex_attrib_array(2);
        gl.vertex_attrib_pointer_with_i32(2, 4, GL::FLOAT, false, instance_stride, color_offset);
        gl.vertex_attrib_divisor(2, 1);

        gl.enable_vertex_attrib_array(3);
        gl.vertex_attrib_pointer_with_i32(3, 3, GL::FLOAT, false, instance_stride, 0);
        gl.vertex_attrib_divisor(3, 1);

        gl.enable_vertex_attrib_array(4);
        gl.vertex_attrib_pointer_with_i32(
            4,
            3,
            GL::FLOAT,
            false,
            instance_stride,
            (3 * std::mem::size_of::<f32>()) as i32,
        );
        gl.vertex_attrib_divisor(4, 1);

        gl.enable_vertex_attrib_array(5);
        gl.vertex_attrib_pointer_with_i32(
            5,
            3,
            GL::FLOAT,
            false,
            instance_stride,
            (6 * std::mem::size_of::<f32>()) as i32,
        );
        gl.vertex_attrib_divisor(5, 1);

        let uv_rect_offset = (9 * std::mem::size_of::<f32>()) as i32;
        gl.enable_vertex_attrib_array(6);
        gl.vertex_attrib_pointer_with_i32(6, 4, GL::FLOAT, false, instance_stride, uv_rect_offset);
        gl.vertex_attrib_divisor(6, 1);

        gl.bind_vertex_array(None);
        gl.bind_buffer(GL::ARRAY_BUFFER, None);

        // Create a 1x1 white texture for UI bars (texture * color = color)
        let white_tex = gl.create_texture().ok_or("Failed to create white tex")?;
        gl.bind_texture(GL::TEXTURE_2D, Some(&white_tex));
        gl.tex_image_2d_with_i32_and_i32_and_i32_and_format_and_type_and_opt_u8_array(
            GL::TEXTURE_2D, 0, GL::RGBA as i32, 1, 1, 0,
            GL::RGBA, GL::UNSIGNED_BYTE, Some(&[255, 255, 255, 255]),
        ).map_err(|_| "Failed to upload white tex")?;
        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MIN_FILTER, GL::NEAREST as i32);
        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MAG_FILTER, GL::NEAREST as i32);

        Ok(Self {
            shader,
            vao,
            _quad_vbo: quad_vbo,
            instance_vbo,
            white_tex,
        })
    }

    /// Draw a filled bar (HP, stamina, etc.).
    pub fn draw_bar(
        &self,
        gl: &GL,
        x: f32,
        y: f32,
        width: f32,
        height: f32,
        fill_ratio: f32,
        bg_color: [f32; 4],
        fill_color: [f32; 4],
        projection: &[f32; 16],
    ) {
        self.shader.bind(gl);
        self.shader.uniform_matrix4fv(gl, "u_projection", projection);

        // Bind white texture so tex_color = white, output = vertex color
        gl.active_texture(GL::TEXTURE0);
        gl.bind_texture(GL::TEXTURE_2D, Some(&self.white_tex));
        self.shader.uniform_1i(gl, "u_texture", 0);

        // Build two instances: background (full width) and foreground (filled portion)
        let bg =
            InstanceData::new(x, y, width, height, [0.0, 0.0, 1.0, 1.0], bg_color);
        let fg_w = width * fill_ratio.clamp(0.0, 1.0);
        let fg_x = x - width * 0.5 + fg_w * 0.5;
        let fg = InstanceData::new(fg_x, y, fg_w, height, [0.0, 0.0, 1.0, 1.0], fill_color);

        let instances: [InstanceData; 2] = [bg, fg];
        let data: &[u8] = unsafe {
            std::slice::from_raw_parts(
                instances.as_ptr() as *const u8,
                std::mem::size_of_val(&instances),
            )
        };

        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&self.instance_vbo));
        gl.buffer_sub_data_with_i32_and_u8_array(GL::ARRAY_BUFFER, 0, data);

        gl.bind_vertex_array(Some(&self.vao));
        gl.draw_arrays_instanced(GL::TRIANGLE_FAN, 0, 4, 2);
        gl.bind_vertex_array(None);
        gl.bind_buffer(GL::ARRAY_BUFFER, None);
    }

    /// Get screen-space orthographic projection (pixel coords, origin top-left).
    pub fn screen_projection(width: f32, height: f32) -> [f32; 16] {
        [
            2.0 / width, 0.0, 0.0, 0.0, 0.0, -2.0 / height, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, -1.0,
            1.0, 0.0, 1.0,
        ]
    }
}
