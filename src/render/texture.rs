use web_sys::WebGl2RenderingContext as GL;

pub struct Texture {
    pub raw: web_sys::WebGlTexture,
    pub width: u32,
    pub height: u32,
}

impl Texture {
    pub fn from_rgba(gl: &GL, data: &[u8], width: u32, height: u32) -> Result<Self, String> {
        let tex: web_sys::WebGlTexture = gl.create_texture().ok_or("Failed to create texture")?;
        gl.bind_texture(GL::TEXTURE_2D, Some(&tex));
        gl.tex_image_2d_with_i32_and_i32_and_i32_and_format_and_type_and_opt_u8_array(
            GL::TEXTURE_2D,
            0,
            GL::RGBA as i32,
            width as i32,
            height as i32,
            0,
            GL::RGBA,
            GL::UNSIGNED_BYTE,
            Some(data),
        )
        .map_err(|e| format!("tex_image_2d failed: {:?}", e))?;

        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MIN_FILTER, GL::NEAREST as i32);
        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MAG_FILTER, GL::NEAREST as i32);
        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_WRAP_S, GL::CLAMP_TO_EDGE as i32);
        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_WRAP_T, GL::CLAMP_TO_EDGE as i32);
        gl.bind_texture(GL::TEXTURE_2D, None);

        Ok(Self { raw: tex, width, height })
    }

    pub fn bind(&self, gl: &GL, unit: u32) {
        gl.active_texture(GL::TEXTURE0 + unit);
        gl.bind_texture(GL::TEXTURE_2D, Some(&self.raw));
    }

    pub fn id(&self) -> u32 {
        let js_val: &wasm_bindgen::JsValue = self.raw.as_ref();
        std::ptr::from_ref(js_val) as *const () as u32
    }
}
