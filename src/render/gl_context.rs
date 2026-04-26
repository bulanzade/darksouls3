use wasm_bindgen::JsCast;
use web_sys::WebGl2RenderingContext;

pub struct GlContext {
    pub gl: WebGl2RenderingContext,
}

impl GlContext {
    pub fn from_canvas_id(canvas_id: &str) -> Result<Self, String> {
        let document = web_sys::window()
            .ok_or("No window")?
            .document()
            .ok_or("No document")?;
        let canvas = document
            .get_element_by_id(canvas_id)
            .ok_or(format!("Canvas element '{}' not found", canvas_id))?;
        let canvas: web_sys::HtmlCanvasElement =
            canvas.dyn_into().map_err(|_| "Element is not a canvas")?;

        let gl: WebGl2RenderingContext = canvas
            .get_context("webgl2")
            .map_err(|_| "Failed to get webgl2 context")?
            .ok_or("WebGL2 not supported")?
            .dyn_into()
            .map_err(|_| "Context is not WebGL2")?;

        gl.enable(WebGl2RenderingContext::DEPTH_TEST);
        gl.enable(WebGl2RenderingContext::BLEND);
        gl.blend_func(
            WebGl2RenderingContext::SRC_ALPHA,
            WebGl2RenderingContext::ONE_MINUS_SRC_ALPHA,
        );

        Ok(Self { gl })
    }

    pub fn clear(&self, r: f32, g: f32, b: f32, a: f32) {
        let gl = &self.gl;
        gl.clear_color(r, g, b, a);
        gl.clear(
            WebGl2RenderingContext::COLOR_BUFFER_BIT | WebGl2RenderingContext::DEPTH_BUFFER_BIT,
        );
    }

    pub fn set_viewport(&self, width: i32, height: i32) {
        self.gl.viewport(0, 0, width, height);
    }
}
