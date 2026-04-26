use web_sys::WebGl2RenderingContext as GL;

use crate::render::shader::ShaderProgram;
use crate::render::texture::Texture;
use crate::render::vertex::{InstanceData, MAX_INSTANCES, QUAD_INDICES, QUAD_VERTICES, SpriteVertex};

pub struct SpriteBatcher {
    vao: web_sys::WebGlVertexArrayObject,
    _quad_vbo: web_sys::WebGlBuffer,
    _ebo: web_sys::WebGlBuffer,
    instance_vbo: web_sys::WebGlBuffer,
    shader: ShaderProgram,
    instances: Vec<InstanceData>,
    current_texture: Option<web_sys::WebGlTexture>,
    current_texture_id: Option<u32>,
}

impl SpriteBatcher {
    pub fn new(gl: &GL) -> Result<Self, String> {
        let vert_src = include_str!("../../static/shaders/sprite.vert");
        let frag_src = include_str!("../../static/shaders/sprite.frag");

        let mut shader = ShaderProgram::compile(gl, vert_src, frag_src)?;
        shader.cache_uniform(gl, "u_projection");
        shader.cache_uniform(gl, "u_texture");

        // Create VAO
        let vao = gl
            .create_vertex_array()
            .ok_or("Failed to create VAO")?;
        gl.bind_vertex_array(Some(&vao));

        // Quad VBO — holds the 4 corner vertices shared by every instance
        let quad_vbo = gl.create_buffer().ok_or("Failed to create quad VBO")?;
        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&quad_vbo));

        let vertex_bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                QUAD_VERTICES.as_ptr() as *const u8,
                std::mem::size_of_val(&QUAD_VERTICES),
            )
        };
        gl.buffer_data_with_u8_array(GL::ARRAY_BUFFER, vertex_bytes, GL::STATIC_DRAW);

        let vertex_stride = std::mem::size_of::<SpriteVertex>() as i32;

        // Location 0: a_pos (vec2)
        gl.enable_vertex_attrib_array(0);
        gl.vertex_attrib_pointer_with_i32(0, 2, GL::FLOAT, false, vertex_stride, 0);

        // Location 1: a_uv (vec2)
        gl.enable_vertex_attrib_array(1);
        gl.vertex_attrib_pointer_with_i32(
            1,
            2,
            GL::FLOAT,
            false,
            vertex_stride,
            (2 * std::mem::size_of::<f32>()) as i32,
        );

        // EBO — two triangles forming a quad
        let ebo = gl.create_buffer().ok_or("Failed to create EBO")?;
        gl.bind_buffer(GL::ELEMENT_ARRAY_BUFFER, Some(&ebo));

        let index_bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                QUAD_INDICES.as_ptr() as *const u8,
                std::mem::size_of_val(&QUAD_INDICES),
            )
        };
        gl.buffer_data_with_u8_array(GL::ELEMENT_ARRAY_BUFFER, index_bytes, GL::STATIC_DRAW);

        // Instance VBO — pre-allocated for MAX_INSTANCES
        let instance_vbo = gl
            .create_buffer()
            .ok_or("Failed to create instance VBO")?;
        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&instance_vbo));

        let instance_buf_size = (MAX_INSTANCES * std::mem::size_of::<InstanceData>()) as i32;
        gl.buffer_data_with_i32(GL::ARRAY_BUFFER, instance_buf_size, GL::DYNAMIC_DRAW);

        let instance_stride = std::mem::size_of::<InstanceData>() as i32;

        // InstanceData memory layout:
        //   offset  0: transform [f32; 9] — 36 bytes
        //   offset 36: uv_rect   [f32; 4] — 16 bytes  (not consumed by current shader)
        //   offset 52: color     [f32; 4] — 16 bytes
        //
        // Shader expects:
        //   location 2: a_color     (vec4) at offset 52
        //   location 3: a_transform (mat3) columns at offset 0 (locations 3,4,5)

        let color_offset = (13 * std::mem::size_of::<f32>()) as i32; // transform(9) + uv_rect(4)
        gl.enable_vertex_attrib_array(2);
        gl.vertex_attrib_pointer_with_i32(2, 4, GL::FLOAT, false, instance_stride, color_offset);
        gl.vertex_attrib_divisor(2, 1);

        // a_transform column 0 — offset 0
        gl.enable_vertex_attrib_array(3);
        gl.vertex_attrib_pointer_with_i32(3, 3, GL::FLOAT, false, instance_stride, 0);
        gl.vertex_attrib_divisor(3, 1);

        // a_transform column 1 — offset 12
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

        // a_transform column 2 — offset 24
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

        // a_uv_rect (vec4) — offset 36 (= 9 floats), instanced
        let uv_rect_offset = (9 * std::mem::size_of::<f32>()) as i32;
        gl.enable_vertex_attrib_array(6);
        gl.vertex_attrib_pointer_with_i32(6, 4, GL::FLOAT, false, instance_stride, uv_rect_offset);
        gl.vertex_attrib_divisor(6, 1);

        // Unbind
        gl.bind_vertex_array(None);
        gl.bind_buffer(GL::ARRAY_BUFFER, None);

        Ok(Self {
            vao,
            _quad_vbo: quad_vbo,
            _ebo: ebo,
            instance_vbo,
            shader,
            instances: Vec::with_capacity(MAX_INSTANCES),
            current_texture: None,
            current_texture_id: None,
        })
    }

    /// Queue a sprite instance. Flushes automatically when the texture changes
    /// or when the instance buffer is full.
    pub fn draw(&mut self, instance: InstanceData, texture: &Texture, gl: &GL) {
        let tex_id = texture.id();

        // Texture change — flush current batch first
        if self.current_texture_id.is_some() && self.current_texture_id != Some(tex_id) {
            self.flush(gl);
        }

        self.current_texture_id = Some(tex_id);
        self.current_texture = Some(texture.raw.clone());
        self.instances.push(instance);

        if self.instances.len() >= MAX_INSTANCES {
            self.flush(gl);
        }
    }

    /// Upload queued instances and issue an instanced draw call.
    pub fn flush(&mut self, gl: &GL) {
        if self.instances.is_empty() {
            return;
        }

        let instance_bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                self.instances.as_ptr() as *const u8,
                self.instances.len() * std::mem::size_of::<InstanceData>(),
            )
        };

        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&self.instance_vbo));
        gl.buffer_sub_data_with_i32_and_u8_array(GL::ARRAY_BUFFER, 0, instance_bytes);

        // Bind the current texture to unit 0
        if let Some(ref tex) = self.current_texture {
            gl.active_texture(GL::TEXTURE0);
            gl.bind_texture(GL::TEXTURE_2D, Some(tex));
        }

        self.shader.bind(gl);
        self.shader.uniform_1i(gl, "u_texture", 0);

        gl.bind_vertex_array(Some(&self.vao));
        gl.draw_elements_instanced_with_i32(
            GL::TRIANGLES,
            QUAD_INDICES.len() as i32,
            GL::UNSIGNED_SHORT,
            0,
            self.instances.len() as i32,
        );
        gl.bind_vertex_array(None);

        self.instances.clear();
        self.current_texture = None;
        self.current_texture_id = None;
    }

    /// Set the projection uniform (call once after creation or on resize).
    pub fn set_projection(&self, gl: &GL, projection: &[f32; 16]) {
        self.shader.bind(gl);
        self.shader.uniform_matrix4fv(gl, "u_projection", projection);
    }
}
