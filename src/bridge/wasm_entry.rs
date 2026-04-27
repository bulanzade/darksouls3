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

    // Create enemies
    let enemies = vec![
        Enemy::new_hollow_soldier(2, 100.0, 100.0),
        Enemy::new_hollow_soldier(3, 400.0, 100.0),
        Enemy::new_hollow_soldier(4, 400.0, 400.0),
    ];

    // Initial lights
    let lights = vec![
        Light { x: 256.0, y: 256.0, radius: 200.0, color: [0.9, 0.8, 0.6], intensity: 0.4 },
        Light { x: 100.0, y: 100.0, radius: 150.0, color: [0.3, 0.3, 0.8], intensity: 0.2 },
    ];

    let game = Game {
        gl_ctx,
        batcher,
        texture,
        time: Time::new(),
        input: InputState::new(),
        camera: {
            let mut cam = Camera2D::new(screen_w, screen_h);
            cam.x = 256.0;
            cam.y = 256.0;
            cam
        },
        player: Player::new(1, 256.0, 256.0),
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

fn create_tileset_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let width: u32 = 64;
    let height: u32 = 16;
    let mut data = vec![0u8; (width * height * 4) as usize];

    let tile_colors: [[u8; 4]; 4] = [
        [0, 0, 0, 0],
        [139, 90, 43, 255],
        [100, 100, 100, 255],
        [60, 60, 60, 255],
    ];

    for tile_idx in 0..4u32 {
        let tile_x_offset = tile_idx * 16;
        let color = tile_colors[tile_idx as usize];
        for ty in 0..16u32 {
            for tx in 0..16u32 {
                let px = tile_x_offset + tx;
                let py = ty;
                let offset = ((py * width + px) * 4) as usize;
                data[offset] = color[0];
                data[offset + 1] = color[1];
                data[offset + 2] = color[2];
                data[offset + 3] = color[3];
            }
        }
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
                    game.player = Player::new(1, 256.0, 256.0);
                    game.enemies = vec![
                        Enemy::new_hollow_soldier(2, 100.0, 100.0),
                        Enemy::new_hollow_soldier(3, 400.0, 100.0),
                        Enemy::new_hollow_soldier(4, 400.0, 400.0),
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
    }

    // Boss AI update
    if let Some(ref mut boss) = game.boss {
        if !boss.is_dead() {
            boss.update_ai(px, py, dt);
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
                damage: 50,
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

        if *boss.state() == EntityState::Attacking && dist < 60.0 && !boss.has_hit_this_attack {
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
        game.boss = Some(Boss::new_test_boss(10, 400.0, 300.0));
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
                    game.player = Player::new(1, 256.0, 256.0);
                    game.souls = 0; // Lost souls
                    game.bonfire.rest();
                    game.enemies = vec![
                        Enemy::new_hollow_soldier(2, 100.0, 100.0),
                        Enemy::new_hollow_soldier(3, 400.0, 100.0),
                        Enemy::new_hollow_soldier(4, 400.0, 400.0),
                    ];
                    game.boss = None;
                    game.boss_active = false;
                    game.boss_defeated = false;
                    game.time.accumulator = 0.0;
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

fn render(game: &mut Game) {
    let gl = &game.gl_ctx.gl;
    game.gl_ctx.clear(0.02, 0.02, 0.04, 1.0);

    let projection = game.camera.projection_matrix();
    game.batcher.set_projection(gl, &projection);

    // --- Draw tilemap ---
    let (off_x, off_y) = game.chunk.world_offset();
    let tile_size = TILE_SIZE as f32;

    for y in 0..crate::world::chunk::CHUNK_SIZE {
        for x in 0..crate::world::chunk::CHUNK_SIZE {
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

    // --- Draw enemies ---
    for enemy in &game.enemies {
        enemy.render(&mut game.batcher, &game.texture, gl);
    }

    // --- Draw boss ---
    if let Some(ref boss) = game.boss {
        boss.render(&mut game.batcher, &game.texture, gl);
    }

    // --- Draw player ---
    game.player.render(&mut game.batcher, &game.texture, gl);

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

    // --- Menu overlay bars (background darkening for title/death) ---
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

    // Death title
    if let Some(el) = document.get_element_by_id("death-title") {
        if game.state == GameState::DeathScreen {
            let _ = el.set_attribute("style", "");
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
        el.set_text_content(Some(&format!(
            "HP {}/{} | STA {}/{} | {}",
            hp, max_hp, stamina, max_sta, state_name
        )));
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
