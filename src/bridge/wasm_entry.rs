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
        Enemy::new_hollow_soldier(2, 180.0, 180.0),
        Enemy::new_hollow_soldier(3, 350.0, 200.0),
        Enemy::new_hollow_soldier(4, 150.0, 380.0),
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
        camera: Camera2D::new(screen_w, screen_h),
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

    // Keyboard event listeners
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

    log::info!("DS2D initialized — WASD/arrows to move, Space to roll, J to attack, E for estus");
    request_next_frame();
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
        game.input.begin_frame();
        fixed_update(game, fixed_dt);
    }

    render(game);
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
                    game.player = Player::new(1, 256.0, 256.0);
                    game.enemies = vec![
                        Enemy::new_hollow_soldier(2, 180.0, 180.0),
                        Enemy::new_hollow_soldier(3, 350.0, 200.0),
                        Enemy::new_hollow_soldier(4, 150.0, 380.0),
                    ];
                    game.boss = None;
                    game.boss_active = false;
                    game.boss_defeated = false;
                    game.souls = 0;
                    game.bonfire = BonfireState::new();
                }
                MenuAction::Continue => {
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

        if *enemy.state() == EntityState::Attacking && dist < enemy.attack_range {
            if *game.player.state() != EntityState::Rolling {
                let dmg = DamageInfo {
                    damage: enemy.damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: 10.0,
                    attacker_id: enemy.id(),
                };
                game.player.take_damage(&dmg);
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

        if *boss.state() == EntityState::Attacking && dist < 60.0 {
            if *game.player.state() != EntityState::Rolling {
                let dmg = DamageInfo {
                    damage: boss.damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: 15.0,
                    attacker_id: boss.id(),
                };
                game.player.take_damage(&dmg);
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
                        Enemy::new_hollow_soldier(2, 180.0, 180.0),
                        Enemy::new_hollow_soldier(3, 350.0, 200.0),
                        Enemy::new_hollow_soldier(4, 150.0, 380.0),
                    ];
                    game.boss = None;
                    game.boss_active = false;
                    game.boss_defeated = false;
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

    // --- Lighting pass ---
    let light_proj = game.camera.projection_matrix();
    let (_cam_x, _cam_y) = (game.camera.x, game.camera.y);
    game.light_renderer.render_lights(
        gl,
        &game.lights,
        &light_proj,
        game.screen_w,
        game.screen_h,
    );

    // --- Post-processing pass ---
    game.post_processor.render(
        gl,
        0.4,                                    // vignette
        [0.02, 0.02, 0.04, 0.3],               // fog color
        [300.0, 500.0],                          // fog distance
        0.95,                                    // brightness
        0.9,                                     // saturation
    );

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

    // --- Menu overlays ---
    match game.state {
        GameState::TitleScreen => {
            draw_menu_overlay(gl, &game.ui_renderer, &ui_proj, &game.menu, game.screen_w, game.screen_h);
        }
        GameState::DeathScreen => {
            // Darken screen
            game.ui_renderer.draw_bar(
                gl, game.screen_w * 0.5, game.screen_h * 0.5,
                game.screen_w, game.screen_h,
                1.0,
                [0.0, 0.0, 0.0, 0.7],
                [0.0, 0.0, 0.0, 0.7],
                &ui_proj,
            );
            draw_menu_overlay(gl, &game.ui_renderer, &ui_proj, &game.menu, game.screen_w, game.screen_h);
        }
        GameState::BonfireMenu => {
            draw_menu_overlay(gl, &game.ui_renderer, &ui_proj, &game.menu, game.screen_w, game.screen_h);
        }
        _ => {}
    }
}

fn draw_menu_overlay(
    gl: &web_sys::WebGl2RenderingContext,
    ui: &UiRenderer,
    proj: &[f32; 16],
    menu: &MenuState,
    screen_w: f32,
    screen_h: f32,
) {
    // Dark background for menu
    ui.draw_bar(
        gl,
        screen_w * 0.5,
        screen_h * 0.5,
        screen_w,
        screen_h,
        1.0,
        [0.0, 0.0, 0.0, 0.5],
        [0.0, 0.0, 0.0, 0.5],
        proj,
    );

    // Menu items as bars
    let item_h = 24.0;
    let spacing = 32.0;
    let start_y = screen_h * 0.5 - (menu.items.len() as f32 * spacing) * 0.5;

    for (i, _item) in menu.items.iter().enumerate() {
        let y = start_y + i as f32 * spacing;
        let is_selected = i == menu.selected_index;
        let color: [f32; 4] = if is_selected {
            [0.9, 0.8, 0.3, 0.9]
        } else {
            [0.5, 0.5, 0.5, 0.7]
        };
        ui.draw_bar(
            gl,
            screen_w * 0.5,
            y,
            160.0,
            item_h,
            1.0,
            [0.1, 0.1, 0.1, 0.6],
            color,
            proj,
        );
    }
}
