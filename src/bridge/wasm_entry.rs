use crate::render::gl_context::GlContext;
use wasm_bindgen::prelude::*;

static mut GL_CONTEXT: Option<GlContext> = None;

#[wasm_bindgen(start)]
pub fn wasm_main() {
    console_error_panic_hook::set_once();

    let gl_ctx = GlContext::from_canvas_id("game-canvas").expect("Failed to init WebGL2");
    gl_ctx.set_viewport(960, 540);

    unsafe {
        GL_CONTEXT = Some(gl_ctx);
    }

    log::info!("DS2D initialized");
    start_game_loop();
}

fn start_game_loop() {
    let f = Closure::wrap(Box::new(|| {
        unsafe {
            let ctx_ptr = &raw const GL_CONTEXT;
            if let Some(gl) = &*ctx_ptr {
                gl.clear(0.05, 0.05, 0.08, 1.0);
            }
        }
        request_next_frame();
    }) as Box<dyn FnMut()>);

    web_sys::window()
        .unwrap()
        .request_animation_frame(&f.into_js_value().unchecked_ref())
        .unwrap();
}

fn request_next_frame() {
    let f = Closure::wrap(Box::new(|| {
        unsafe {
            let ctx_ptr = &raw const GL_CONTEXT;
            if let Some(gl) = &*ctx_ptr {
                gl.clear(0.05, 0.05, 0.08, 1.0);
            }
        }
        request_next_frame();
    }) as Box<dyn FnMut()>);

    web_sys::window()
        .unwrap()
        .request_animation_frame(&f.into_js_value().unchecked_ref())
        .unwrap();
}
