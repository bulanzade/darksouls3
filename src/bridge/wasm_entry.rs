use crate::render::gl_context::GlContext;
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use crate::render::vertex::InstanceData;
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;

struct Game {
    gl_ctx: GlContext,
    batcher: SpriteBatcher,
    texture: Texture,
    frame: u32,
}

static mut GAME: Option<Game> = None;

#[wasm_bindgen(start)]
pub fn wasm_main() {
    console_error_panic_hook::set_once();

    let gl_ctx = GlContext::from_canvas_id("game-canvas").expect("Failed to init WebGL2");
    gl_ctx.set_viewport(960, 540);

    let gl = &gl_ctx.gl;

    let batcher = SpriteBatcher::new(gl).expect("Failed to create sprite batcher");
    let projection = orthographic(-480.0, 480.0, -270.0, 270.0, -1.0, 1.0);
    batcher.set_projection(gl, &projection);

    let texture = create_test_texture(gl);

    let game = Game {
        gl_ctx,
        batcher,
        texture,
        frame: 0,
    };

    unsafe {
        GAME = Some(game);
    }

    log::info!("DS2D initialized with sprite batcher");
    request_next_frame();
}

fn create_test_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let size: u32 = 16;
    let mut data = Vec::with_capacity((size * size * 4) as usize);

    for y in 0..size {
        for x in 0..size {
            let checker = ((x / 8) + (y / 8)) % 2 == 0;
            if checker {
                data.extend_from_slice(&[0xFF, 0x00, 0xFF, 0xFF]); // magenta
            } else {
                data.extend_from_slice(&[0x80, 0x00, 0x80, 0xFF]); // dark purple
            }
        }
    }

    Texture::from_rgba(gl, &data, size, size).expect("Failed to create test texture")
}

fn orthographic(left: f32, right: f32, bottom: f32, top: f32, near: f32, far: f32) -> [f32; 16] {
    let tx = -(right + left) / (right - left);
    let ty = -(top + bottom) / (top - bottom);
    let tz = -(far + near) / (far - near);
    [
        2.0 / (right - left), 0.0, 0.0, 0.0,
        0.0, 2.0 / (top - bottom), 0.0, 0.0,
        0.0, 0.0, -2.0 / (far - near), 0.0,
        tx, ty, tz, 1.0,
    ]
}

fn request_next_frame() {
    let f = Closure::wrap(Box::new(|| {
        unsafe {
            let game_ptr = &raw mut GAME;
            if let Some(g) = &mut *game_ptr {
                tick(g);
            }
        }
        request_next_frame();
    }) as Box<dyn FnMut()>);

    web_sys::window()
        .unwrap()
        .request_animation_frame(&f.into_js_value().unchecked_ref())
        .unwrap();
}

fn tick(game: &mut Game) {
    let gl = &game.gl_ctx.gl;
    game.gl_ctx.clear(0.05, 0.05, 0.08, 1.0);

    // Pulsing colour that cycles over time
    let t = game.frame as f32 * 0.02;
    let pulse = t.sin() * 0.5 + 0.5;
    let color = [pulse, 0.5 + pulse * 0.5, 1.0 - pulse * 0.3, 1.0];

    let instance = InstanceData::new(0.0, 0.0, 64.0, 64.0, [0.0, 0.0, 1.0, 1.0], color);

    game.batcher.draw(instance, &game.texture, gl);
    game.batcher.flush(gl);

    game.frame += 1;
}
