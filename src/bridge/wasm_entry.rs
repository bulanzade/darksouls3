use crate::audio::audio_engine::AudioEngine;
use crate::core::camera::Camera2D;
use crate::core::input::InputState;
use crate::core::input::KeyCode;
use crate::core::time::{Time, FIXED_DT};
use crate::entity::boss::Boss;
use crate::entity::enemy::Enemy;
use crate::entity::entity_trait::{DamageInfo, Entity, EntityState};
use crate::entity::player::Player;
use crate::game::{GameState, MenuAction, MenuState};
use crate::render::gl_context::GlContext;
use crate::render::light_renderer::{Light, LightRenderer};
use crate::render::post_process::PostProcessor;
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use crate::render::ui_renderer::UiRenderer;
use crate::render::vertex::InstanceData;
use crate::save::bonfire::BonfireState;
use crate::world::chunk::Chunk;
use crate::world::collision::CollisionGrid;
use crate::world::tileset::{TileId, Tileset, TILE_SIZE};
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;

struct Game {
    gl_ctx: GlContext,
    batcher: SpriteBatcher,
    texture: Texture,
    player_tex: Texture,
    enemy_tex: Texture,
    boss_tex: Texture,
    white_tex: Texture,
    bonfire_tex: Texture,
    time: Time,
    input: InputState,
    camera: Camera2D,
    player: Player,
    enemies: Vec<Enemy>,
    boss: Option<Boss>,
    chunk: Chunk,
    tileset: Tileset,
    collision: CollisionGrid,
    tileset_texture: Texture,
    // Rendering subsystems
    light_renderer: LightRenderer,
    post_processor: PostProcessor,
    ui_renderer: UiRenderer,
    // Lights
    lights: Vec<Light>,
    // Game state
    state: GameState,
    menu: MenuState,
    // RPG
    souls: u32,
    bonfire: BonfireState,
    audio: AudioEngine,
    // Boss tracking
    boss_active: bool,
    boss_defeated: bool,
    // Grace period after state transition to prevent accidental interactions
    state_timer: f32,
    // Bonfire world position
    bonfire_x: f32,
    bonfire_y: f32,
    // Screen dimensions
    screen_w: f32,
    screen_h: f32,
}

static mut GAME: Option<Game> = None;

#[wasm_bindgen(start)]
pub fn wasm_main() {
    console_error_panic_hook::set_once();

    let gl_ctx = GlContext::from_canvas_id("game-canvas").expect("Failed to init WebGL2");
    let screen_w: f32 = 960.0;
    let screen_h: f32 = 540.0;
    gl_ctx.set_viewport(screen_w as i32, screen_h as i32);

    let gl = &gl_ctx.gl;

    let batcher = SpriteBatcher::new(gl).expect("Failed to create sprite batcher");
    let texture = create_test_texture(gl);
    let tileset = Tileset::test_tileset(64, 16);
    let chunk = Chunk::test_chunk((0, 0));
    let collision = CollisionGrid::from_chunk(&chunk, &tileset);
    let tileset_texture = create_tileset_texture(gl);

    let light_renderer = LightRenderer::new(gl).expect("Failed to create light renderer");
    let post_processor = PostProcessor::new(gl).expect("Failed to create post-processor");
    let ui_renderer = UiRenderer::new(gl).expect("Failed to create UI renderer");

    // Create enemies — placed in Room 2 (Enemy Hall)
    let enemies = vec![
        Enemy::new_hollow_soldier(2, 600.0, 150.0),
        Enemy::new_hollow_soldier(3, 750.0, 200.0),
        Enemy::new_hollow_soldier(4, 680.0, 300.0),
    ];

    // Initial lights
    let lights = vec![
        Light { x: 200.0, y: 200.0, radius: 250.0, color: [0.9, 0.8, 0.6], intensity: 0.4 },
        Light { x: 700.0, y: 200.0, radius: 200.0, color: [0.3, 0.3, 0.8], intensity: 0.2 },
    ];

    let player_tex = create_player_texture(&gl);
    let enemy_tex = create_enemy_texture(&gl);
    let boss_tex = create_boss_texture(&gl);
    let white_tex = create_white_texture(&gl);
    let bonfire_tex = create_bonfire_texture(&gl);

    let game = Game {
        gl_ctx,
        batcher,
        texture,
        player_tex,
        enemy_tex,
        boss_tex,
        white_tex,
        bonfire_tex,
        time: Time::new(),
        input: InputState::new(),
        camera: {
            let mut cam = Camera2D::new(screen_w, screen_h);
            cam.x = 200.0;
            cam.y = 200.0;
            cam
        },
        player: Player::new(1, 200.0, 200.0),
        enemies,
        boss: None,
        chunk,
        tileset,
        collision,
        tileset_texture,
        light_renderer,
        post_processor,
        ui_renderer,
        lights,
        state: GameState::TitleScreen,
        menu: MenuState::title_screen(),
        souls: 0,
        bonfire: BonfireState::new(),
        audio: AudioEngine,
        boss_active: false,
        boss_defeated: false,
        state_timer: 0.0,
        bonfire_x: 200.0,
        bonfire_y: 200.0,
        screen_w,
        screen_h,
    };

    unsafe {
        GAME = Some(game);
    }

    log::info!("DS2D v2 initialized — WASD/arrows to move, Space to roll, J to attack, E for estus");
    request_next_frame();
}

/// Called from JavaScript on keydown. `key` is the KeyboardEvent.key string.
#[wasm_bindgen]
pub fn js_keydown(key: &str) {
    let idx = key_to_idx(key);
    if idx < 256 {
        unsafe {
            let game_ptr = &raw mut GAME;
            if let Some(g) = &mut *game_ptr {
                g.input.set_key(idx, true);
            }
        }
    }
}

/// Called from JavaScript on keyup.
#[wasm_bindgen]
pub fn js_keyup(key: &str) {
    let idx = key_to_idx(key);
    if idx < 256 {
        unsafe {
            let game_ptr = &raw mut GAME;
            if let Some(g) = &mut *game_ptr {
                g.input.set_key(idx, false);
            }
        }
    }
}

/// Returns game state info for debugging.
#[wasm_bindgen]
pub fn js_debug_state() -> String {
    unsafe {
        let game_ptr = &raw mut GAME;
        if let Some(g) = &mut *game_ptr {
            let state = match g.state {
                GameState::TitleScreen => "TitleScreen",
                GameState::Playing => "Playing",
                GameState::DeathScreen => "DeathScreen",
                GameState::BonfireMenu => "BonfireMenu",
                GameState::Victory => "Victory",
                _ => "Other",
            };
            let enemies: Vec<String> = g.enemies.iter().enumerate().map(|(i, e)| {
                let (ex, ey) = e.position();
                let dist = ((g.player.transform.x - ex).powi(2) + (g.player.transform.y - ey).powi(2)).sqrt();
                format!("{}:({:.0},{:.0}) d={:.0} s={:?}", i, ex, ey, dist, e.state)
            }).collect();
            format!(
                "state={} hp={} inv={} pos=({:.0},{:.0}) enemies=[{}] acc={:.3}",
                state, g.player.hp, g.player.invuln_timer,
                g.player.transform.x, g.player.transform.y,
                enemies.join(" "),
                g.time.accumulator,
            )
        } else {
            "GAME not initialized".into()
        }
    }
}

/// Map KeyboardEvent.key() string to our KeyCode index.
/// Uses the same values as the KeyCode enum so the rest of the code works unchanged.
fn key_to_idx(key: &str) -> usize {
    match key {
        " " => 32,
        "Shift" | "ShiftLeft" => 16,
        "Enter" => 13,
        "Escape" => 27,
        "ArrowLeft" => 37,
        "ArrowUp" => 38,
        "ArrowRight" => 39,
        "ArrowDown" => 40,
        "a" | "A" => 65,
        "d" | "D" => 68,
        "e" | "E" => 69,
        "i" | "I" => 73,
        "j" | "J" => 74,
        "k" | "K" => 75,
        "l" | "L" => 76,
        "s" | "S" => 83,
        "w" | "W" => 87,
        _ => 255,
    }
}

fn create_test_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let size: u32 = 16;
    let mut data = Vec::with_capacity((size * size * 4) as usize);

    for y in 0..size {
        for x in 0..size {
            let checker = ((x / 8) + (y / 8)) % 2 == 0;
            if checker {
                data.extend_from_slice(&[0xFF, 0x00, 0xFF, 0xFF]);
            } else {
                data.extend_from_slice(&[0x80, 0x00, 0x80, 0xFF]);
            }
        }
    }

    Texture::from_rgba(gl, &data, size, size).expect("Failed to create test texture")
}

fn create_player_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    // 16x16 knight sprite
    let mut data = vec![0u8; 16 * 16 * 4];
    let set = |data: &mut Vec<u8>, x: u32, y: u32, r: u8, g: u8, b: u8, a: u8| {
        let i = ((y * 16 + x) * 4) as usize;
        data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
    };
    // Helmet (silver)
    for x in 6..10 { set(&mut data, x, 1, 180, 180, 200, 255); }
    for x in 5..11 { set(&mut data, x, 2, 160, 160, 180, 255); }
    for x in 5..11 { set(&mut data, x, 3, 140, 140, 160, 255); }
    // Visor
    set(&mut data, 6, 2, 40, 40, 60, 255);
    set(&mut data, 9, 2, 40, 40, 60, 255);
    set(&mut data, 7, 3, 40, 40, 60, 255);
    set(&mut data, 8, 3, 40, 40, 60, 255);
    // Face
    for x in 6..10 { set(&mut data, x, 4, 220, 180, 140, 255); }
    // Body (armor)
    for y in 5..9 { for x in 5..11 { set(&mut data, x, y, 100, 100, 120, 255); } }
    // Belt
    for x in 5..11 { set(&mut data, x, 8, 80, 60, 30, 255); }
    // Legs
    for y in 9..12 { set(&mut data, 6, y, 80, 80, 90, 255); set(&mut data, 9, y, 80, 80, 90, 255); }
    // Sword (right side)
    for y in 2..10 { set(&mut data, 12, y, 200, 200, 210, 255); }
    set(&mut data, 11, 5, 160, 140, 60, 255); // guard
    set(&mut data, 13, 5, 160, 140, 60, 255); // guard
    // Shield (left side)
    for y in 4..8 { for x in 2..5 { set(&mut data, x, y, 60, 80, 140, 255); } }
    // Boots
    for y in 12..14 { set(&mut data, 5, y, 60, 50, 40, 255); set(&mut data, 6, y, 60, 50, 40, 255); }
    for y in 12..14 { set(&mut data, 9, y, 60, 50, 40, 255); set(&mut data, 10, y, 60, 50, 40, 255); }
    Texture::from_rgba(gl, &data, 16, 16).expect("Failed to create player texture")
}

fn create_enemy_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    // 16x16 hollow soldier sprite
    let mut data = vec![0u8; 16 * 16 * 4];
    let set = |data: &mut Vec<u8>, x: u32, y: u32, r: u8, g: u8, b: u8, a: u8| {
        let i = ((y * 16 + x) * 4) as usize;
        data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
    };
    // Head (pale, hollow)
    for x in 6..10 { set(&mut data, x, 2, 100, 90, 80, 255); }
    for x in 5..11 { set(&mut data, x, 3, 90, 80, 70, 255); }
    for x in 5..11 { set(&mut data, x, 4, 110, 95, 80, 255); }
    // Hollow eyes
    set(&mut data, 6, 3, 20, 20, 20, 255); set(&mut data, 9, 3, 20, 20, 20, 255);
    // Torn body
    for y in 5..9 { for x in 5..11 { set(&mut data, x, y, 70, 60, 50, 255); } }
    // Rags
    set(&mut data, 5, 6, 80, 70, 55, 255); set(&mut data, 10, 7, 80, 70, 55, 255);
    // Legs
    for y in 9..12 { set(&mut data, 6, y, 60, 55, 45, 255); set(&mut data, 9, y, 60, 55, 45, 255); }
    // Sword
    for y in 3..8 { set(&mut data, 12, y, 140, 140, 140, 255); }
    set(&mut data, 11, 5, 100, 80, 40, 255);
    // Boots
    for y in 12..14 { set(&mut data, 5, y, 50, 45, 35, 255); set(&mut data, 6, y, 50, 45, 35, 255); }
    for y in 12..14 { set(&mut data, 9, y, 50, 45, 35, 255); set(&mut data, 10, y, 50, 45, 35, 255); }
    Texture::from_rgba(gl, &data, 16, 16).expect("Failed to create enemy texture")
}

fn create_boss_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    // 24x24 demon boss sprite
    let s = 24u32;
    let mut data = vec![0u8; (s * s * 4) as usize];
    let set = |data: &mut Vec<u8>, x: u32, y: u32, r: u8, g: u8, b: u8, a: u8| {
        let i = ((y * s + x) * 4) as usize;
        data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
    };
    // Horns
    set(&mut data, 6, 0, 80, 20, 20, 255); set(&mut data, 5, 1, 80, 20, 20, 255);
    set(&mut data, 17, 0, 80, 20, 20, 255); set(&mut data, 18, 1, 80, 20, 20, 255);
    // Head
    for x in 8..16 { set(&mut data, x, 2, 60, 15, 15, 255); }
    for x in 7..17 { for y in 3..6 { set(&mut data, x, y, 70, 20, 25, 255); } }
    // Glowing eyes
    set(&mut data, 9, 4, 255, 200, 50, 255); set(&mut data, 10, 4, 255, 200, 50, 255);
    set(&mut data, 13, 4, 255, 200, 50, 255); set(&mut data, 14, 4, 255, 200, 50, 255);
    // Mouth
    for x in 10..14 { set(&mut data, x, 5, 40, 10, 10, 255); }
    // Torso
    for x in 6..18 { for y in 6..14 { set(&mut data, x, y, 55, 15, 20, 255); } }
    // Armor plates
    for x in 8..16 { for y in 7..10 { set(&mut data, x, y, 80, 30, 35, 255); } }
    // Arms
    for y in 7..12 { set(&mut data, 4, y, 60, 20, 25, 255); set(&mut data, 5, y, 60, 20, 25, 255); }
    for y in 7..12 { set(&mut data, 18, y, 60, 20, 25, 255); set(&mut data, 19, y, 60, 20, 25, 255); }
    // Weapon (great sword)
    for y in 1..14 { set(&mut data, 21, y, 150, 150, 160, 255); set(&mut data, 22, y, 130, 130, 140, 255); }
    set(&mut data, 20, 8, 120, 100, 40, 255); set(&mut data, 23, 8, 120, 100, 40, 255);
    // Legs
    for y in 14..20 { set(&mut data, 8, y, 50, 15, 18, 255); set(&mut data, 9, y, 50, 15, 18, 255); }
    for y in 14..20 { set(&mut data, 14, y, 50, 15, 18, 255); set(&mut data, 15, y, 50, 15, 18, 255); }
    // Feet
    for y in 20..22 { for x in 7..11 { set(&mut data, x, y, 40, 12, 12, 255); } }
    for y in 20..22 { for x in 13..17 { set(&mut data, x, y, 40, 12, 12, 255); } }
    Texture::from_rgba(gl, &data, s, s).expect("Failed to create boss texture")
}

fn create_white_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let data: [u8; 4] = [0xFF, 0xFF, 0xFF, 0xFF];
    Texture::from_rgba(gl, &data, 1, 1).expect("Failed to create white texture")
}

fn create_bonfire_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    // 32x32 bonfire sprite with coals and flames
    let s: u32 = 32;
    let mut data = vec![0u8; (s * s * 4) as usize];
    let set = |data: &mut Vec<u8>, x: u32, y: u32, r: u8, g: u8, b: u8, a: u8| {
        let i = ((y * s + x) * 4) as usize;
        data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
    };
    // Stone base
    for x in 8..24 { for y in 22..28 {
        let shade = if (x + y) % 3 == 0 { 80 } else { 90 };
        set(&mut data, x, y, shade, shade, shade + 10, 255);
    }}
    // Darker stone edges
    for x in 8..24 {
        set(&mut data, x, 21, 60, 60, 65, 255);
        set(&mut data, x, 28, 60, 60, 65, 255);
    }
    for y in 21..29 {
        set(&mut data, 7, y, 60, 60, 65, 255);
        set(&mut data, 24, y, 60, 60, 65, 255);
    }
    // Coals (glowing embers)
    for x in 10..22 { for y in 20..23 {
        let glow = if (x * 7 + y * 13) % 5 < 2 { 255 } else { 200 };
        set(&mut data, x, y, glow, glow / 3, 0, 255);
    }}
    // Flame core (inner bright)
    for x in 13..19 { for y in 12..20 {
        set(&mut data, x, y, 255, 220, 100, 255);
    }}
    // Flame mid (orange)
    for x in 12..20 { for y in 8..16 {
        let a = if (x + y) % 3 == 0 { 200 } else { 255 };
        set(&mut data, x, y, 255, 140, 20, a);
    }}
    // Flame outer (red-orange)
    for x in 11..21 { for y in 6..12 {
        let a = if (x * 3 + y * 7) % 4 < 2 { 180 } else { 230 };
        set(&mut data, x, y, 220, 80, 10, a);
    }}
    // Flame tips
    set(&mut data, 14, 5, 200, 60, 10, 200);
    set(&mut data, 15, 4, 180, 50, 10, 160);
    set(&mut data, 16, 3, 160, 40, 5, 120);
    set(&mut data, 17, 4, 180, 50, 10, 160);
    set(&mut data, 18, 5, 200, 60, 10, 200);
    // Sparks
    set(&mut data, 10, 7, 255, 200, 50, 200);
    set(&mut data, 21, 8, 255, 180, 40, 180);
    set(&mut data, 12, 5, 255, 220, 80, 150);
    set(&mut data, 19, 6, 255, 200, 60, 170);
    // Sword inserted in bonfire
    for y in 10..22 { set(&mut data, 15, y, 160, 160, 170, 255); set(&mut data, 16, y, 140, 140, 150, 255); }
    // Blade reflection in fire
    set(&mut data, 15, 14, 200, 180, 100, 255);
    set(&mut data, 16, 15, 200, 180, 100, 255);

    Texture::from_rgba(gl, &data, s, s).expect("Failed to create bonfire texture")
}

fn create_tileset_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let width: u32 = 64;
    let height: u32 = 16;
    let mut data = vec![0u8; (width * height * 4) as usize];

    let set_px = |data: &mut Vec<u8>, px: u32, py: u32, r: u8, g: u8, b: u8, a: u8| {
        let offset = ((py * width + px) * 4) as usize;
        data[offset] = r; data[offset+1] = g; data[offset+2] = b; data[offset+3] = a;
    };

    // Tile 0: Empty (transparent) — already zeros

    // Tile 1: Ground — dark stone floor with variation and cracks
    {
        let tx_off = 1 * 16;
        for ty in 0..16u32 {
            for tx in 0..16u32 {
                let px = tx_off + tx;
                let noise = ((tx * 7 + ty * 13) % 17) as u8;
                let base_r = 100u8.saturating_add(noise / 3);
                let base_g = 75u8.saturating_add(noise / 4);
                let base_b = 45u8.saturating_add(noise / 5);
                set_px(&mut data, px, ty, base_r, base_g, base_b, 255);
            }
        }
        // Cracks
        for i in 3..9 { set_px(&mut data, tx_off + i, 7, 70, 50, 30, 255); }
        for i in 5..12 { set_px(&mut data, tx_off + i, 11, 65, 45, 25, 255); }
        // Border shadows
        for x in 0..16 { set_px(&mut data, tx_off + x, 0, 85, 60, 35, 255); }
        for y in 0..16 { set_px(&mut data, tx_off, y, 85, 60, 35, 255); }
    }

    // Tile 2: Wall — grey stone blocks with mortar lines
    {
        let tx_off = 2 * 16;
        for ty in 0..16u32 {
            for tx in 0..16u32 {
                let px = tx_off + tx;
                let noise = ((tx * 11 + ty * 7) % 13) as u8;
                let base = 85u8.saturating_add(noise / 2);
                set_px(&mut data, px, ty, base, base, base + 5, 255);
            }
        }
        // Mortar lines (horizontal)
        for x in 0..16 { set_px(&mut data, tx_off + x, 4, 55, 55, 58, 255); }
        for x in 0..16 { set_px(&mut data, tx_off + x, 9, 55, 55, 58, 255); }
        for x in 0..16 { set_px(&mut data, tx_off + x, 14, 55, 55, 58, 255); }
        // Mortar lines (vertical, offset for brick pattern)
        for y in 0..4 { set_px(&mut data, tx_off + 5, y, 55, 55, 58, 255); set_px(&mut data, tx_off + 11, y, 55, 55, 58, 255); }
        for y in 5..9 { set_px(&mut data, tx_off + 3, y, 55, 55, 58, 255); set_px(&mut data, tx_off + 8, y, 55, 55, 58, 255); set_px(&mut data, tx_off + 13, y, 55, 55, 58, 255); }
        for y in 10..14 { set_px(&mut data, tx_off + 6, y, 55, 55, 58, 255); set_px(&mut data, tx_off + 12, y, 55, 55, 58, 255); }
        // Top highlight
        for x in 0..16 { set_px(&mut data, tx_off + x, 0, 105, 105, 110, 255); }
    }

    // Tile 3: Dark wall / decoration with moss
    {
        let tx_off = 3 * 16;
        for ty in 0..16u32 {
            for tx in 0..16u32 {
                let px = tx_off + tx;
                let noise = ((tx * 5 + ty * 9) % 11) as u8;
                let base = 50u8.saturating_add(noise / 3);
                set_px(&mut data, px, ty, base, base, base + 3, 255);
            }
        }
        // Moss patches
        for x in 2..6 { set_px(&mut data, tx_off + x, 14, 40, 55, 35, 255); set_px(&mut data, tx_off + x, 15, 35, 50, 30, 255); }
        for x in 10..14 { set_px(&mut data, tx_off + x, 13, 40, 55, 35, 255); }
    }

    Texture::from_rgba(gl, &data, width, height).expect("Failed to create tileset texture")
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
        fixed_update(game, fixed_dt);
    }

    render(game);

    // Clear press flags AFTER game logic has consumed them
    game.input.begin_frame();
}

fn fixed_update(game: &mut Game, dt: f32) {
    match game.state {
        GameState::TitleScreen => update_title_screen(game),
        GameState::Playing => update_playing(game, dt),
        GameState::DeathScreen => update_death(game),
        GameState::BonfireMenu => update_bonfire_menu(game),
        GameState::Victory => update_victory(game),
        _ => {}
    }
}

fn update_title_screen(game: &mut Game) {
    if game.input.pressed(KeyCode::Enter) {
        if let Some(action) = game.menu.current_action() {
            match action {
                MenuAction::NewGame => {
                    game.state = GameState::Playing;
                    game.time.accumulator = 0.0;
                    game.state_timer = 0.0;
                    game.player = Player::new(1, 200.0, 200.0);
                    game.enemies = vec![
                        Enemy::new_hollow_soldier(2, 620.0, 160.0),
                        Enemy::new_hollow_soldier(3, 740.0, 200.0),
                        Enemy::new_hollow_soldier(4, 680.0, 320.0),
                    ];
                    game.boss = None;
                    game.boss_active = false;
                    game.boss_defeated = false;
                    game.souls = 0;
                    game.bonfire = BonfireState::new();
                }
                MenuAction::Continue => {
                    game.state = GameState::Playing;
                    game.time.accumulator = 0.0;
                    game.state_timer = 0.0;
                }
                _ => {}
            }
        }
    }
    if game.input.pressed(KeyCode::Up) {
        game.menu.move_up();
    }
    if game.input.pressed(KeyCode::Down) {
        game.menu.move_down();
    }
}

fn update_playing(game: &mut Game, dt: f32) {
    let mv = game.input.movement();
    let attack = game.input.pressed(KeyCode::J);
    let roll = game.input.pressed(KeyCode::Space);
    let estus = game.input.pressed(KeyCode::E);
    let interact = game.input.pressed(KeyCode::Enter);

    // Bonfire interaction (skip for first 0.5s after state change)
    if interact && game.state_timer > 0.5 {
        let (px, py) = game.player.position();
        let dx = px - game.bonfire_x;
        let dy = py - game.bonfire_y;
        let dist = (dx * dx + dy * dy).sqrt();
        if dist < 40.0 {
            game.state = GameState::BonfireMenu;
            game.menu = MenuState::bonfire_menu();
            game.time.accumulator = 0.0;
            return;
        }
    }

    // Tick state transition timer
    game.state_timer += dt;

    // Estus healing
    if estus && game.player.hp < game.player.max_hp {
        let heal = game.bonfire.use_estus();
        if heal > 0 {
            game.player.hp = (game.player.hp + heal).min(game.player.max_hp);
        }
    }

    // Player input
    {
        let player = &mut game.player;
        match player.state {
            EntityState::Idle | EntityState::Moving => {
                if mv.0 != 0.0 || mv.1 != 0.0 {
                    player.facing = mv.1.atan2(mv.0);
                    player.state = EntityState::Moving;
                } else {
                    player.state = EntityState::Idle;
                }
                if roll {
                    if player.stamina.consume(25.0) {
                        player.state = EntityState::Rolling;
                        player.roll_timer = player.roll_duration;
                    }
                }
                if attack {
                    if player.stamina.consume(20.0) {
                        player.state = EntityState::Attacking;
                        player.attack_timer = player.attack_duration;
                    }
                }
            }
            _ => {}
        }
    }

    game.player.update(dt);

    // Collision resolution
    let chunk_offset = game.chunk.world_offset();
    let (px, py) = game.player.position();
    let (rx, ry) = game.collision.resolve_aabb(chunk_offset, px, py, 16.0, 16.0);
    game.player.set_position(rx, ry);

    // Enemy AI updates
    let (px, py) = game.player.position();
    for enemy in &mut game.enemies {
        if enemy.is_dead() {
            continue;
        }
        enemy.update_ai(px, py, dt);
        if enemy.flash_timer > 0.0 {
            enemy.flash_timer -= dt;
        }
    }

    // Boss AI update
    if let Some(ref mut boss) = game.boss {
        if !boss.is_dead() {
            boss.update_ai(px, py, dt);
        }
        if boss.flash_timer > 0.0 {
            boss.flash_timer -= dt;
        }
    }

    // --- Combat: player vs enemies ---
    let (px, py) = game.player.position();
    let player_attacking = *game.player.state() == EntityState::Attacking && game.player.attack_timer > 0.0;

    for enemy in &mut game.enemies {
        if enemy.is_dead() {
            continue;
        }
        let (ex, ey) = enemy.position();
        let dist = ((px - ex) * (px - ex) + (py - ey) * (py - ey)).sqrt();

        if player_attacking && dist < 40.0 {
            let dmg = DamageInfo {
                damage: 50,
                knockback_x: 0.0,
                knockback_y: 0.0,
                poise_damage: 20.0,
                attacker_id: game.player.id(),
            };
            enemy.take_damage(&dmg);
            if enemy.is_dead() {
                game.souls += 100;
            }
        }

        if *enemy.state() == EntityState::Attacking && dist < enemy.attack_range && !enemy.has_hit_this_attack {
            if *game.player.state() != EntityState::Rolling {
                let dmg = DamageInfo {
                    damage: enemy.damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: 10.0,
                    attacker_id: enemy.id(),
                };
                game.player.take_damage(&dmg);
                enemy.has_hit_this_attack = true;
            }
        }
    }

    // --- Combat: player vs boss ---
    if let Some(ref mut boss) = game.boss {
        let (bx, by) = boss.position();
        let dist = ((px - bx) * (px - bx) + (py - by) * (py - by)).sqrt();

        if player_attacking && dist < 56.0 {
            let dmg = DamageInfo {
                damage: 100,
                knockback_x: 0.0,
                knockback_y: 0.0,
                poise_damage: 20.0,
                attacker_id: game.player.id(),
            };
            boss.take_damage(&dmg);
            if boss.is_dead() && !game.boss_defeated {
                game.boss_defeated = true;
                game.souls += 5000;
            }
        }

        if *boss.state() == EntityState::Attacking && dist < 48.0 && !boss.has_hit_this_attack {
            if *game.player.state() != EntityState::Rolling {
                let dmg = DamageInfo {
                    damage: boss.damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: 15.0,
                    attacker_id: boss.id(),
                };
                game.player.take_damage(&dmg);
                boss.has_hit_this_attack = true;
            }
        }
    }

    // --- Spawn boss when all enemies dead ---
    if !game.boss_active && !game.boss_defeated && game.enemies.iter().all(|e| e.is_dead()) {
        game.boss = Some(Boss::new_test_boss(10, 736.0, 688.0));
        game.boss_active = true;
    }

    // --- Update lights to follow player ---
    if !game.lights.is_empty() {
        game.lights[0].x = px;
        game.lights[0].y = py;
    }

    // Camera follows player
    game.camera.follow(px, py, 5.0, dt);
    game.camera.update(dt);

    // Audio listener position
    game.audio.set_listener_position(px, py);

    // Check victory
    if game.boss_defeated {
        if let Some(ref boss) = game.boss {
            if boss.is_dead() {
                game.state = GameState::Victory;
            }
        }
    }

    // Check player death
    if game.player.is_dead() {
        game.state = GameState::DeathScreen;
        game.menu = MenuState::death_screen();
    }
}

fn update_death(game: &mut Game) {
    if game.input.pressed(KeyCode::Enter) {
        if let Some(action) = game.menu.current_action() {
            match action {
                MenuAction::Continue => {
                    // Respawn at bonfire
                    game.player = Player::new(1, 200.0, 200.0);
                    game.souls = 0; // Lost souls
                    game.bonfire.rest();
                    game.enemies = vec![
                        Enemy::new_hollow_soldier(2, 620.0, 160.0),
                        Enemy::new_hollow_soldier(3, 740.0, 200.0),
                        Enemy::new_hollow_soldier(4, 680.0, 320.0),
                    ];
                    game.boss = None;
                    game.boss_active = false;
                    game.boss_defeated = false;
                    game.time.accumulator = 0.0;
                    game.state_timer = 0.0;
                    game.state = GameState::Playing;
                }
                MenuAction::QuitToTitle => {
                    game.state = GameState::TitleScreen;
                    game.menu = MenuState::title_screen();
                }
                _ => {}
            }
        }
    }
    if game.input.pressed(KeyCode::Up) {
        game.menu.move_up();
    }
    if game.input.pressed(KeyCode::Down) {
        game.menu.move_down();
    }
}

fn update_bonfire_menu(game: &mut Game) {
    if game.input.pressed(KeyCode::Escape) {
        game.state = GameState::Playing;
        return;
    }
    if game.input.pressed(KeyCode::Enter) {
        if let Some(action) = game.menu.current_action() {
            match action {
                MenuAction::Rest => {
                    game.bonfire.rest();
                    game.player.hp = game.player.max_hp;
                }
                MenuAction::Resume => {
                    game.state = GameState::Playing;
                }
                _ => {}
            }
        }
    }
    if game.input.pressed(KeyCode::Up) {
        game.menu.move_up();
    }
    if game.input.pressed(KeyCode::Down) {
        game.menu.move_down();
    }
}

fn update_victory(game: &mut Game) {
    if game.input.pressed(KeyCode::Enter) {
        game.state = GameState::TitleScreen;
        game.menu = MenuState::title_screen();
        game.boss_active = false;
        game.boss_defeated = false;
        game.boss = None;
        game.souls = 0;
        game.time.accumulator = 0.0;
    }
}

fn render(game: &mut Game) {
    let gl = &game.gl_ctx.gl;
    game.gl_ctx.clear(0.02, 0.02, 0.04, 1.0);

    let projection = game.camera.projection_matrix();
    game.batcher.set_projection(gl, &projection);

    // --- Draw tilemap (only visible tiles) ---
    let (off_x, off_y) = game.chunk.world_offset();
    let tile_size = TILE_SIZE as f32;
    let cam_x = game.camera.x;
    let cam_y = game.camera.y;
    let half_w = game.screen_w * 0.5 + tile_size;
    let half_h = game.screen_h * 0.5 + tile_size;

    let min_tx = (((cam_x - half_w - off_x) / tile_size).floor() as i32).max(0);
    let max_tx = (((cam_x + half_w - off_x) / tile_size).ceil() as i32).min(crate::world::chunk::CHUNK_SIZE as i32 - 1);
    let min_ty = (((cam_y - half_h - off_y) / tile_size).floor() as i32).max(0);
    let max_ty = (((cam_y + half_h - off_y) / tile_size).ceil() as i32).min(crate::world::chunk::CHUNK_SIZE as i32 - 1);

    for y in min_ty as usize..=max_ty as usize {
        for x in min_tx as usize..=max_tx as usize {
            let tile_id = game.chunk.tiles[y][x];
            if tile_id == TileId::Empty {
                continue;
            }
            let def = match game.tileset.get(tile_id) {
                Some(d) => d,
                None => continue,
            };
            let px = off_x + x as f32 * tile_size + tile_size * 0.5;
            let py = off_y + y as f32 * tile_size + tile_size * 0.5;
            let instance = InstanceData::new(
                px,
                py,
                tile_size,
                tile_size,
                [def.uv_x, def.uv_y, def.uv_x + def.uv_w, def.uv_y + def.uv_h],
                [1.0, 1.0, 1.0, 1.0],
            );
            game.batcher.draw(instance, &game.tileset_texture, gl);
        }
    }

    // --- Draw bonfire ---
    {
        let bonfire_data = InstanceData::new(
            game.bonfire_x, game.bonfire_y,
            32.0, 32.0,
            [0.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
        );
        game.batcher.draw(bonfire_data, &game.bonfire_tex, gl);
    }

    // --- Draw enemies ---
    for enemy in &game.enemies {
        if !enemy.is_dead() {
            enemy.render(&mut game.batcher, &game.enemy_tex, gl);
            // Health bar above enemy
            let (ex, ey) = enemy.position();
            let hp_ratio = enemy.hp as f32 / enemy.max_hp as f32;
            let bar_w = 26.0;
            let bar_h = 3.0;
            let bar_y = ey - 20.0;
            // Background
            game.batcher.draw(
                InstanceData::new(ex, bar_y, bar_w, bar_h, [0.0, 0.0, 1.0, 1.0], [0.2, 0.2, 0.2, 0.8]),
                &game.white_tex, gl,
            );
            // Foreground
            let fg_w = bar_w * hp_ratio;
            let fg_x = ex - bar_w * 0.5 + fg_w * 0.5;
            let hp_color: [f32; 4] = if hp_ratio > 0.5 {
                [0.2, 0.8, 0.2, 0.9]
            } else if hp_ratio > 0.25 {
                [0.8, 0.8, 0.2, 0.9]
            } else {
                [0.9, 0.2, 0.2, 0.9]
            };
            game.batcher.draw(
                InstanceData::new(fg_x, bar_y, fg_w, bar_h, [0.0, 0.0, 1.0, 1.0], hp_color),
                &game.white_tex, gl,
            );
        }
    }

    // --- Draw boss ---
    if let Some(ref boss) = game.boss {
        if !boss.is_dead() {
            boss.render(&mut game.batcher, &game.boss_tex, gl);
            // Health bar above boss
            let (bx, by) = boss.position();
            let hp_ratio = boss.hp as f32 / boss.max_hp as f32;
            let bar_w = 48.0;
            let bar_h = 4.0;
            let bar_y = by - 34.0;
            game.batcher.draw(
                InstanceData::new(bx, bar_y, bar_w, bar_h, [0.0, 0.0, 1.0, 1.0], [0.2, 0.2, 0.2, 0.8]),
                &game.white_tex, gl,
            );
            let fg_w = bar_w * hp_ratio;
            let fg_x = bx - bar_w * 0.5 + fg_w * 0.5;
            game.batcher.draw(
                InstanceData::new(fg_x, bar_y, fg_w, bar_h, [0.0, 0.0, 1.0, 1.0], [0.8, 0.2, 0.8, 0.9]),
                &game.white_tex, gl,
            );
        }
    }

    // --- Draw player ---
    game.player.render(&mut game.batcher, &game.player_tex, gl);

    // --- Draw attack swing effect ---
    if *game.player.state() == EntityState::Attacking {
        let (px, py) = game.player.position();
        let facing = game.player.facing;
        let swing_offset = 24.0;
        let sx = px + facing.cos() * swing_offset;
        let sy = py + facing.sin() * swing_offset;
        game.batcher.draw(
            InstanceData::new(sx, sy, 20.0, 20.0, [0.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.6, 0.4]),
            &game.white_tex, gl,
        );
    }

    game.batcher.flush(gl);

    // TODO: re-enable lighting and post-processing once framebuffer is set up.
    // Without a render-to-texture FBO, these passes draw over the scene incorrectly.
    // game.light_renderer.render_lights(...);
    // game.post_processor.render(...);

    // --- HUD (screen-space) ---
    let ui_proj = UiRenderer::screen_projection(game.screen_w, game.screen_h);

    // HP bar
    let hp_ratio = game.player.hp as f32 / game.player.max_hp as f32;
    game.ui_renderer.draw_bar(
        gl, 20.0, 20.0, 200.0, 16.0,
        hp_ratio,
        [0.15, 0.15, 0.15, 0.8],
        [0.7, 0.1, 0.1, 0.9],
        &ui_proj,
    );

    // Stamina bar
    let stamina_ratio = game.player.stamina.current / game.player.stamina.maximum;
    game.ui_renderer.draw_bar(
        gl, 20.0, 42.0, 200.0, 12.0,
        stamina_ratio,
        [0.15, 0.15, 0.15, 0.8],
        [0.1, 0.5, 0.1, 0.9],
        &ui_proj,
    );

    // Boss HP bar (center top)
    if let Some(ref boss) = game.boss {
        if !boss.is_dead() {
            let boss_hp_ratio = boss.hp as f32 / boss.max_hp as f32;
            let boss_bar_w = 400.0;
            let boss_bar_x = (game.screen_w - boss_bar_w) * 0.5;
            game.ui_renderer.draw_bar(
                gl, boss_bar_x, 20.0, boss_bar_w, 14.0,
                boss_hp_ratio,
                [0.15, 0.15, 0.15, 0.8],
                [0.8, 0.2, 0.8, 0.9],
                &ui_proj,
            );
        }
    }

    // Estus indicator
    let estus_ratio = game.bonfire.estus_charges as f32 / game.bonfire.estus_max as f32;
    game.ui_renderer.draw_bar(
        gl, 20.0, 58.0, 60.0, 10.0,
        if estus_ratio > 0.0 { 1.0 } else { 0.0 },
        [0.15, 0.15, 0.15, 0.8],
        [0.9, 0.7, 0.1, 0.9],
        &ui_proj,
    );

    // --- Menu overlay bars (background darkening for title/death/victory) ---
    match game.state {
        GameState::TitleScreen => {
            game.ui_renderer.draw_bar(
                gl, game.screen_w * 0.5, game.screen_h * 0.5,
                game.screen_w, game.screen_h,
                1.0,
                [0.0, 0.0, 0.0, 0.5],
                [0.0, 0.0, 0.0, 0.5],
                &ui_proj,
            );
        }
        GameState::DeathScreen => {
            game.ui_renderer.draw_bar(
                gl, game.screen_w * 0.5, game.screen_h * 0.5,
                game.screen_w, game.screen_h,
                1.0,
                [0.0, 0.0, 0.0, 0.7],
                [0.0, 0.0, 0.0, 0.7],
                &ui_proj,
            );
        }
        GameState::Victory => {
            game.ui_renderer.draw_bar(
                gl, game.screen_w * 0.5, game.screen_h * 0.5,
                game.screen_w, game.screen_h,
                1.0,
                [0.0, 0.0, 0.0, 0.6],
                [0.0, 0.0, 0.0, 0.6],
                &ui_proj,
            );
        }
        _ => {}
    }

    // --- DOM text overlay ---
    update_dom_ui(game);
}

fn update_dom_ui(game: &Game) {
    let window = match web_sys::window() {
        Some(w) => w,
        None => return,
    };
    let document = match window.document() {
        Some(d) => d,
        None => return,
    };

    // Menu
    if let Some(menu_el) = document.get_element_by_id("menu") {
        if matches!(game.state, GameState::TitleScreen | GameState::DeathScreen | GameState::BonfireMenu) {
            let html: String = game.menu.items.iter().enumerate().map(|(i, item)| {
                if i == game.menu.selected_index {
                    format!("<div class=\"menu-item selected\">▸ {}</div>", item.label)
                } else {
                    format!("<div class=\"menu-item\">{}</div>", item.label)
                }
            }).collect::<Vec<_>>().join("");
            let _ = menu_el.set_attribute("style", "");
            menu_el.set_inner_html(&html);
        } else {
            let _ = menu_el.set_attribute("style", "display:none");
            menu_el.set_inner_html("");
        }
    }

    // Death title / Victory title
    if let Some(el) = document.get_element_by_id("death-title") {
        if game.state == GameState::DeathScreen {
            el.set_text_content(Some("YOU DIED"));
            let _ = el.set_attribute("style", "");
        } else if game.state == GameState::Victory {
            el.set_text_content(Some(&format!(
                "VICTORY\nSouls: {}\nPress Enter to return to title",
                game.souls
            )));
            let _ = el.set_attribute("style", "color: #e8c840; text-shadow: 0 0 20px rgba(232,200,64,0.6);");
        } else {
            let _ = el.set_attribute("style", "display:none");
        }
    }

    // HUD text
    if let Some(el) = document.get_element_by_id("hud-text") {
        let hp = game.player.hp;
        let max_hp = game.player.max_hp;
        let stamina = game.player.stamina.current as i32;
        let max_sta = game.player.stamina.maximum as i32;
        let state_name = match game.player.state {
            EntityState::Idle => "Idle",
            EntityState::Moving => "Moving",
            EntityState::Attacking => "ATTACK",
            EntityState::Rolling => "ROLL",
            EntityState::Staggered => "STAGGER",
            EntityState::Dead => "DEAD",
            EntityState::Blocking => "BLOCK",
        };
        let mut text = format!(
            "HP {}/{} | STA {}/{} | {}",
            hp, max_hp, stamina, max_sta, state_name
        );
        // Bonfire proximity hint
        if game.state == GameState::Playing {
            let (px, py) = game.player.position();
            let dx = px - game.bonfire_x;
            let dy = py - game.bonfire_y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < 40.0 {
                text.push_str(" | [Enter] Bonfire");
            }
        }
        el.set_text_content(Some(&text));
    }

    // Souls
    if let Some(el) = document.get_element_by_id("souls-text") {
        el.set_text_content(Some(&format!("Souls: {} | Estus: {}/{}",
            game.souls, game.bonfire.estus_charges, game.bonfire.estus_max)));
    }

    // Boss name
    if let Some(el) = document.get_element_by_id("boss-name") {
        if let Some(ref boss) = game.boss {
            if !boss.is_dead() {
                let _ = el.set_attribute("style", "");
                el.set_text_content(Some(&format!("BOSS — HP: {}/{}", boss.hp, boss.max_hp)));
            } else {
                let _ = el.set_attribute("style", "display:none");
            }
        } else {
            let _ = el.set_attribute("style", "display:none");
        }
    }
}
