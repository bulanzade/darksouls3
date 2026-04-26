use crate::core::camera::Camera2D;
use crate::core::input::InputState;
use crate::core::time::{Time, FIXED_DT};
use crate::core::transform::Transform;
use crate::render::gl_context::GlContext;
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;

struct Game {
    gl_ctx: GlContext,
    batcher: SpriteBatcher,
    texture: Texture,
    time: Time,
    input: InputState,
    camera: Camera2D,
    player: Transform,
    player_speed: f32,
}

static mut GAME: Option<Game> = None;

#[wasm_bindgen(start)]
pub fn wasm_main() {
    console_error_panic_hook::set_once();

    let gl_ctx = GlContext::from_canvas_id("game-canvas").expect("Failed to init WebGL2");
    gl_ctx.set_viewport(960, 540);

    let gl = &gl_ctx.gl;

    let batcher = SpriteBatcher::new(gl).expect("Failed to create sprite batcher");
    let texture = create_test_texture(gl);

    let game = Game {
        gl_ctx,
        batcher,
        texture,
        time: Time::new(),
        input: InputState::new(),
        camera: Camera2D::new(960.0, 540.0),
        player: Transform::new(0.0, 0.0),
        player_speed: 120.0,
    };

    unsafe {
        GAME = Some(game);
    }

    // --- Keyboard event listeners ---
    let window = web_sys::window().unwrap();

    let keydown_closure = Closure::wrap(Box::new(|e: web_sys::KeyboardEvent| {
        let code = e.key_code() as usize;
        unsafe {
            let game_ptr = &raw mut GAME;
            if let Some(g) = &mut *game_ptr {
                g.input.set_key(code, true);
            }
        }
    }) as Box<dyn FnMut(web_sys::KeyboardEvent)>);

    window
        .add_event_listener_with_callback("keydown", keydown_closure.as_ref().unchecked_ref())
        .unwrap();
    keydown_closure.into_js_value();

    let keyup_closure = Closure::wrap(Box::new(|e: web_sys::KeyboardEvent| {
        let code = e.key_code() as usize;
        unsafe {
            let game_ptr = &raw mut GAME;
            if let Some(g) = &mut *game_ptr {
                g.input.set_key(code, false);
            }
        }
    }) as Box<dyn FnMut(web_sys::KeyboardEvent)>);

    window
        .add_event_listener_with_callback("keyup", keyup_closure.as_ref().unchecked_ref())
        .unwrap();
    keyup_closure.into_js_value();

    log::info!("DS2D initialized — WASD/arrows to move");
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

fn request_next_frame() {
    let f = Closure::wrap(Box::new(|timestamp_ms: f64| {
        unsafe {
            let game_ptr = &raw mut GAME;
            if let Some(g) = &mut *game_ptr {
                tick(g, timestamp_ms);
            }
        }
        request_next_frame();
    }) as Box<dyn FnMut(f64)>);

    web_sys::window()
        .unwrap()
        .request_animation_frame(&f.into_js_value().unchecked_ref())
        .unwrap();
}

fn tick(game: &mut Game, timestamp_ms: f64) {
    game.time.update(timestamp_ms);

    let fixed_dt = FIXED_DT as f32;

    while game.time.should_fixed_update() {
        game.input.begin_frame();
        fixed_update(game, fixed_dt);
    }

    render(game);
}

fn fixed_update(game: &mut Game, dt: f32) {
    let (dx, dy) = game.input.movement();
    game.player.x += dx * game.player_speed * dt;
    game.player.y += dy * game.player_speed * dt;

    game.camera.follow(game.player.x, game.player.y, 5.0, dt);
    game.camera.update(dt);
}

fn render(game: &mut Game) {
    let gl = &game.gl_ctx.gl;
    game.gl_ctx.clear(0.05, 0.05, 0.08, 1.0);

    let projection = game.camera.projection_matrix();
    game.batcher.set_projection(gl, &projection);

    let instance = game.player.to_instance_data(
        64.0,
        64.0,
        [0.0, 0.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
    );

    game.batcher.draw(instance, &game.texture, gl);
    game.batcher.flush(gl);
}
