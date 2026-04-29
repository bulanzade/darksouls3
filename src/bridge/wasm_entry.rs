use crate::audio::audio_engine::AudioEngine;
use crate::core::camera::Camera2D;
use crate::core::input::InputState;
use crate::core::input::KeyCode;
use crate::core::time::{Time, FIXED_DT};
use crate::ai::state_machine::{STAGGERED, RANGED_ATTACK};
use crate::entity::boss::Boss;
use crate::entity::enemy::Enemy;
use crate::entity::entity_trait::{DamageInfo, Entity, EntityId, EntityState};
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
use crate::save::save_manager::{self, SaveData};
use crate::world::chunk::{Chunk, CHUNK_SIZE};
use crate::world::collision::CollisionGrid;
use crate::world::nav_grid::NavGrid;
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
    nav_grid: NavGrid,
    tileset_texture: Texture,
    // Rendering subsystems
    light_renderer: LightRenderer,
    post_processor: PostProcessor,
    ui_renderer: UiRenderer,
    // Framebuffer for post-processing
    scene_fbo: web_sys::WebGlFramebuffer,
    scene_texture: web_sys::WebGlTexture,
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
    // Lock-on targeting
    lock_on_target: Option<EntityId>,
    // Grace period after state transition to prevent accidental interactions
    state_timer: f32,
    // Bonfire world position
    bonfire_x: f32,
    bonfire_y: f32,
    // Screen dimensions
    screen_w: f32,
    screen_h: f32,
    // Bloodstain (soul retrieval)
    bloodstain_x: f32,
    bloodstain_y: f32,
    bloodstain_souls: u32,
    has_bloodstain: bool,
    // Soul orbs (floating particles from enemy kills)
    soul_orbs: Vec<SoulOrb>,
    // World item pickups
    items: Vec<WorldItem>,
    // Enemy projectiles (arrows)
    projectiles: Vec<Projectile>,
    // Death animation timer (fades in over 2s)
    death_anim_timer: f32,
    // Boss intro text timer (fades out over 3s)
    boss_intro_timer: f32,
    // Heal particle effect timer
    heal_effect_timer: f32,
    // Block spark effects (visual feedback for knight blocking)
    block_sparks: Vec<BlockSpark>,
    // Dust particles from rolls and impacts
    dust_particles: Vec<DustParticle>,
    // Screen flash (parry, critical hit)
    screen_flash: Option<ScreenFlash>,
    // Stagger burst effects on enemies
    stagger_bursts: Vec<BlockSpark>,
    // Parry riposte window timer
    riposte_timer: f32,
    riposte_target_id: EntityId,
    // Floating damage numbers
    damage_numbers: Vec<DamageNumber>,
    // Enemy death dissolve particles
    death_particles: Vec<DeathParticle>,
    // Level-up flash timer
    level_up_flash: f32,
    // Hitstop (freeze frames on heavy hit)
    hitstop_timer: f32,
    // Slow motion on boss death
    slow_motion_timer: f32,
    // Input buffer for queued actions
    input_buffer: BufferedAction,
    input_buffer_timer: f32,
    // Game statistics
    enemies_killed: u32,
    damage_dealt: u32,
    damage_taken: u32,
    death_count: u32,
    play_time: f32,
    // Treasure chests
    chests: Vec<TreasureChest>,
    // NPCs
    npcs: Vec<Npc>,
}

struct WorldItem {
    x: f32,
    y: f32,
    kind: ItemKind,
    collected: bool,
}

enum ItemKind {
    SoulOrb(u32),      // grants N souls
    EstusShard,         // increases max estus by 1
    HomewardBone,       // unused for now
    PurpleMoss,         // cures poison
    WeaponDrop(crate::combat::weapon::WeaponType),
}

struct SoulOrb {
    x: f32,
    y: f32,
    vy: f32,
    timer: f32,
    max_time: f32,
}

struct Projectile {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    damage: i32,
    timer: f32,
}

struct BlockSpark {
    x: f32,
    y: f32,
    timer: f32,
}

struct DustParticle {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    timer: f32,
}

struct ScreenFlash {
    timer: f32,
    max_timer: f32,
    color: [f32; 4],
}

struct DamageNumber {
    x: f32,
    y: f32,
    vy: f32,
    value: i32,
    timer: f32,
    is_player_damage: bool,
}

struct DeathParticle {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    timer: f32,
    size: f32,
}

#[derive(Clone, Copy, PartialEq)]
enum BufferedAction {
    Attack,
    HeavyAttack,
    Roll,
    None,
}

struct TreasureChest {
    x: f32,
    y: f32,
    opened: bool,
    loot: ItemKind,
}

struct Npc {
    x: f32,
    y: f32,
    name: String,
    color: [f32; 4],
    dialogue: Vec<String>,
    dialogue_index: usize,
    talking: bool,
    kind: NpcKind,
}

#[derive(Clone, Copy, PartialEq)]
enum NpcKind {
    LevelUp,      // Emerald Herald — spend souls to level up
    Merchant,     // Buy items with souls
    Blacksmith,   // Upgrade weapons
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
    let tileset = Tileset::test_tileset(80, 16);
    let chunk = Chunk::test_chunk((0, 0));
    let collision = CollisionGrid::from_chunk(&chunk, &tileset);
    let nav_grid = NavGrid::from_collision_grid(&collision, CHUNK_SIZE, 2);
    let tileset_texture = create_tileset_texture(gl);

    let light_renderer = LightRenderer::new(gl).expect("Failed to create light renderer");
    let post_processor = PostProcessor::new(gl).expect("Failed to create post-processor");
    let ui_renderer = UiRenderer::new(gl).expect("Failed to create UI renderer");

    // Create off-screen FBO for post-processing
    let (scene_fbo, scene_texture) = create_scene_fbo(gl, screen_w, screen_h);

    // Create enemies — placed across the dungeon
    let enemies = vec![
        // Room 2: hollow soldiers + archer
        Enemy::new_hollow_soldier(2, 620.0, 120.0),
        Enemy::new_archer(3, 780.0, 200.0),
        Enemy::new_hollow_soldier(4, 700.0, 320.0),
        // Room 4: archer + soldiers + knight
        Enemy::new_archer(5, 1200.0, 500.0),
        Enemy::new_hollow_soldier(6, 1350.0, 600.0),
        Enemy::new_knight(7, 1450.0, 700.0),
        Enemy::new_hollow_soldier(8, 1250.0, 800.0),
        // Room 5: Mini-boss
        Enemy::new_mini_boss(9, 1264.0, 1280.0),
    ];

    // Initial lights — player torch + ambient torches along corridors
    let lights = vec![
        Light { x: 200.0, y: 200.0, radius: 250.0, color: [0.9, 0.8, 0.6], intensity: 0.4 },
        Light { x: 700.0, y: 200.0, radius: 200.0, color: [0.3, 0.3, 0.8], intensity: 0.2 },
        // Corridor torches
        Light { x: 500.0, y: 300.0, radius: 150.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
        Light { x: 800.0, y: 350.0, radius: 150.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
        // Room 3 torches
        Light { x: 450.0, y: 700.0, radius: 180.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
        Light { x: 700.0, y: 750.0, radius: 180.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
        // Room 4 torches
        Light { x: 1200.0, y: 500.0, radius: 180.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
        Light { x: 1400.0, y: 650.0, radius: 180.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
        // Boss arena torches
        Light { x: 1700.0, y: 300.0, radius: 200.0, color: [0.8, 0.2, 0.4], intensity: 0.2 },
        Light { x: 1800.0, y: 500.0, radius: 200.0, color: [0.8, 0.2, 0.4], intensity: 0.2 },
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
        nav_grid,
        tileset_texture,
        light_renderer,
        post_processor,
        ui_renderer,
        scene_fbo,
        scene_texture,
        lights,
        state: GameState::TitleScreen,
        menu: MenuState::title_screen_with_save_check(),
        souls: 0,
        bonfire: BonfireState::new(),
        audio: AudioEngine,
        boss_active: false,
        boss_defeated: false,
        lock_on_target: None,
        state_timer: 0.0,
        bonfire_x: 200.0,
        bonfire_y: 200.0,
        screen_w,
        screen_h,
        bloodstain_x: 0.0,
        bloodstain_y: 0.0,
        bloodstain_souls: 0,
        has_bloodstain: false,
        soul_orbs: Vec::new(),
        items: vec![
            // Room 3 (Treasure): items
            WorldItem { x: 520.0, y: 700.0, kind: ItemKind::SoulOrb(200), collected: false },
            WorldItem { x: 700.0, y: 800.0, kind: ItemKind::SoulOrb(300), collected: false },
            WorldItem { x: 820.0, y: 650.0, kind: ItemKind::EstusShard, collected: false },
            // Corridors - scattered souls
            WorldItem { x: 1300.0, y: 750.0, kind: ItemKind::SoulOrb(500), collected: false },
            // Boss arena entrance
            WorldItem { x: 1700.0, y: 500.0, kind: ItemKind::SoulOrb(1000), collected: false },
            // Purple moss (cure poison) - near poison area in Room 3
            WorldItem { x: 600.0, y: 750.0, kind: ItemKind::PurpleMoss, collected: false },
            // Second moss near corridor poison
            WorldItem { x: 1100.0, y: 1000.0, kind: ItemKind::PurpleMoss, collected: false },
        ],
        projectiles: Vec::new(),
        death_anim_timer: 0.0,
        boss_intro_timer: 0.0,
        heal_effect_timer: 0.0,
        block_sparks: Vec::new(),
        dust_particles: Vec::new(),
        screen_flash: None,
        stagger_bursts: Vec::new(),
        riposte_timer: 0.0,
        riposte_target_id: 0,
        damage_numbers: Vec::new(),
        death_particles: Vec::new(),
        level_up_flash: 0.0,
        hitstop_timer: 0.0,
        slow_motion_timer: 0.0,
        input_buffer: BufferedAction::None,
        input_buffer_timer: 0.0,
        enemies_killed: 0,
        damage_dealt: 0,
        damage_taken: 0,
        death_count: 0,
        play_time: 0.0,
        chests: vec![
            // Room 3 (Treasure room)
            TreasureChest { x: 480.0, y: 680.0, opened: false, loot: ItemKind::SoulOrb(500) },
            TreasureChest { x: 560.0, y: 780.0, opened: false, loot: ItemKind::EstusShard },
            // Boss arena
            TreasureChest { x: 1780.0, y: 350.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::Uchigatana) },
            // Corridor near poison
            TreasureChest { x: 1000.0, y: 900.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::GreatAxe) },
        ],
        npcs: vec![
            // Emerald Herald at bonfire — level up NPC
            Npc {
                x: 240.0, y: 180.0,
                name: "Emerald Herald".into(),
                color: [0.2, 0.9, 0.7, 1.0],
                dialogue: vec![
                    "Welcome to the land of Drangleic.".into(),
                    "You will lose your souls, again and again.".into(),
                    "But fear not. Seek strength. The rest is up to you.".into(),
                    "[Enter] Level Up".into(),
                ],
                dialogue_index: 0,
                talking: false,
                kind: NpcKind::LevelUp,
            },
            // Merchant in Room 3 — sells items
            Npc {
                x: 580.0, y: 720.0,
                name: "Merchant".into(),
                color: [0.8, 0.7, 0.3, 1.0],
                dialogue: vec![
                    "Heh heh... Something catch your eye?".into(),
                    "I've got estus shards, purple moss...".into(),
                    "All for the low price of your souls.".into(),
                    "[Enter] Buy Estus Shard (500 souls)".into(),
                ],
                dialogue_index: 0,
                talking: false,
                kind: NpcKind::Merchant,
            },
        ],
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
            let lock = match g.lock_on_target {
                Some(tid) => format!(" lock={}", tid),
                None => " lock=none".into(),
            };
            format!(
                "state={} hp={} inv={} pos=({:.0},{:.0}) enemies=[{}] acc={:.3}{}",
                state, g.player.hp, g.player.invuln_timer,
                g.player.transform.x, g.player.transform.y,
                enemies.join(" "),
                g.time.accumulator,
                lock,
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
        "Tab" => 9,
        "w" | "W" => 87,
        "1" => 49,
        "2" => 50,
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
    // 64x16 sprite atlas: 4 frames (idle, walk, attack, block)
    // Each frame is 16x16
    let frame_w: u32 = 16;
    let total_w: u32 = 64;
    let h: u32 = 16;
    let mut data = vec![0u8; (total_w * h * 4) as usize];
    let set = |data: &mut Vec<u8>, frame: u32, x: u32, y: u32, r: u8, g: u8, b: u8, a: u8| {
        let px = frame * frame_w + x;
        let i = ((y * total_w + px) * 4) as usize;
        data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
    };

    // Frame 0: Idle — standing with sword at rest
    {
        let f = 0;
        // Helmet
        for x in 6..10 { set(&mut data, f, x, 1, 180, 180, 200, 255); }
        for x in 5..11 { set(&mut data, f, x, 2, 160, 160, 180, 255); }
        for x in 5..11 { set(&mut data, f, x, 3, 140, 140, 160, 255); }
        set(&mut data, f, 6, 2, 40, 40, 60, 255); set(&mut data, f, 9, 2, 40, 40, 60, 255);
        for x in 6..10 { set(&mut data, f, x, 4, 220, 180, 140, 255); }
        for y in 5..9 { for x in 5..11 { set(&mut data, f, x, y, 100, 100, 120, 255); } }
        for x in 5..11 { set(&mut data, f, x, 8, 80, 60, 30, 255); }
        for y in 9..12 { set(&mut data, f, 6, y, 80, 80, 90, 255); set(&mut data, f, 9, y, 80, 80, 90, 255); }
        for y in 2..10 { set(&mut data, f, 12, y, 200, 200, 210, 255); }
        set(&mut data, f, 11, 5, 160, 140, 60, 255); set(&mut data, f, 13, 5, 160, 140, 60, 255);
        for y in 4..8 { for x in 2..5 { set(&mut data, f, x, y, 60, 80, 140, 255); } }
        for y in 12..14 { set(&mut data, f, 5, y, 60, 50, 40, 255); set(&mut data, f, 6, y, 60, 50, 40, 255); }
        for y in 12..14 { set(&mut data, f, 9, y, 60, 50, 40, 255); set(&mut data, f, 10, y, 60, 50, 40, 255); }
    }

    // Frame 1: Walk — legs spread, slight lean
    {
        let f = 1;
        for x in 6..10 { set(&mut data, f, x, 1, 180, 180, 200, 255); }
        for x in 5..11 { set(&mut data, f, x, 2, 160, 160, 180, 255); }
        for x in 5..11 { set(&mut data, f, x, 3, 140, 140, 160, 255); }
        set(&mut data, f, 6, 2, 40, 40, 60, 255); set(&mut data, f, 9, 2, 40, 40, 60, 255);
        for x in 6..10 { set(&mut data, f, x, 4, 220, 180, 140, 255); }
        for y in 5..9 { for x in 5..11 { set(&mut data, f, x, y, 100, 100, 120, 255); } }
        for x in 5..11 { set(&mut data, f, x, 8, 80, 60, 30, 255); }
        // Legs spread (walking pose)
        for y in 9..12 { set(&mut data, f, 5, y, 80, 80, 90, 255); set(&mut data, f, 10, y, 80, 80, 90, 255); }
        for y in 2..10 { set(&mut data, f, 12, y, 200, 200, 210, 255); }
        set(&mut data, f, 11, 5, 160, 140, 60, 255); set(&mut data, f, 13, 5, 160, 140, 60, 255);
        for y in 4..8 { for x in 2..5 { set(&mut data, f, x, y, 60, 80, 140, 255); } }
        for y in 12..14 { set(&mut data, f, 4, y, 60, 50, 40, 255); set(&mut data, f, 5, y, 60, 50, 40, 255); }
        for y in 12..14 { set(&mut data, f, 10, y, 60, 50, 40, 255); set(&mut data, f, 11, y, 60, 50, 40, 255); }
    }

    // Frame 2: Attack — sword swung forward
    {
        let f = 2;
        for x in 6..10 { set(&mut data, f, x, 1, 180, 180, 200, 255); }
        for x in 5..11 { set(&mut data, f, x, 2, 160, 160, 180, 255); }
        for x in 5..11 { set(&mut data, f, x, 3, 140, 140, 160, 255); }
        set(&mut data, f, 6, 2, 40, 40, 60, 255); set(&mut data, f, 9, 2, 40, 40, 60, 255);
        for x in 6..10 { set(&mut data, f, x, 4, 220, 180, 140, 255); }
        for y in 5..9 { for x in 5..11 { set(&mut data, f, x, y, 100, 100, 120, 255); } }
        for x in 5..11 { set(&mut data, f, x, 8, 80, 60, 30, 255); }
        for y in 9..12 { set(&mut data, f, 6, y, 80, 80, 90, 255); set(&mut data, f, 9, y, 80, 80, 90, 255); }
        // Sword extended forward (horizontal)
        for x in 11..15 { set(&mut data, f, x, 5, 200, 200, 210, 255); }
        set(&mut data, f, 10, 5, 160, 140, 60, 255);
        set(&mut data, f, 11, 4, 160, 140, 60, 255);
        for y in 4..8 { for x in 2..5 { set(&mut data, f, x, y, 60, 80, 140, 255); } }
        for y in 12..14 { set(&mut data, f, 5, y, 60, 50, 40, 255); set(&mut data, f, 6, y, 60, 50, 40, 255); }
        for y in 12..14 { set(&mut data, f, 9, y, 60, 50, 40, 255); set(&mut data, f, 10, y, 60, 50, 40, 255); }
    }

    // Frame 3: Block — shield raised
    {
        let f = 3;
        for x in 6..10 { set(&mut data, f, x, 1, 180, 180, 200, 255); }
        for x in 5..11 { set(&mut data, f, x, 2, 160, 160, 180, 255); }
        for x in 5..11 { set(&mut data, f, x, 3, 140, 140, 160, 255); }
        set(&mut data, f, 6, 2, 40, 40, 60, 255); set(&mut data, f, 9, 2, 40, 40, 60, 255);
        for x in 6..10 { set(&mut data, f, x, 4, 220, 180, 140, 255); }
        for y in 5..9 { for x in 5..11 { set(&mut data, f, x, y, 100, 100, 120, 255); } }
        for x in 5..11 { set(&mut data, f, x, 8, 80, 60, 30, 255); }
        for y in 9..12 { set(&mut data, f, 6, y, 80, 80, 90, 255); set(&mut data, f, 9, y, 80, 80, 90, 255); }
        for y in 2..10 { set(&mut data, f, 12, y, 200, 200, 210, 255); }
        // Shield raised (larger, higher position)
        for y in 2..8 { for x in 1..5 { set(&mut data, f, x, y, 50, 70, 150, 255); } }
        for y in 2..8 { set(&mut data, f, 1, y, 80, 100, 180, 255); }
        for y in 12..14 { set(&mut data, f, 5, y, 60, 50, 40, 255); set(&mut data, f, 6, y, 60, 50, 40, 255); }
        for y in 12..14 { set(&mut data, f, 9, y, 60, 50, 40, 255); set(&mut data, f, 10, y, 60, 50, 40, 255); }
    }

    Texture::from_rgba(gl, &data, total_w, h).expect("Failed to create player texture")
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

fn create_scene_fbo(
    gl: &web_sys::WebGl2RenderingContext,
    width: f32,
    height: f32,
) -> (web_sys::WebGlFramebuffer, web_sys::WebGlTexture) {
    use web_sys::WebGl2RenderingContext as GL;
    let tex = gl.create_texture().unwrap();
    gl.bind_texture(GL::TEXTURE_2D, Some(&tex));
    gl.tex_image_2d_with_i32_and_i32_and_i32_and_format_and_type_and_opt_u8_array(
        GL::TEXTURE_2D, 0, GL::RGBA as i32,
        width as i32, height as i32, 0,
        GL::RGBA, GL::UNSIGNED_BYTE, None,
    ).unwrap();
    gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MIN_FILTER, GL::LINEAR as i32);
    gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MAG_FILTER, GL::LINEAR as i32);
    gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_WRAP_S, GL::CLAMP_TO_EDGE as i32);
    gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_WRAP_T, GL::CLAMP_TO_EDGE as i32);

    let fbo = gl.create_framebuffer().unwrap();
    gl.bind_framebuffer(GL::FRAMEBUFFER, Some(&fbo));
    gl.framebuffer_texture_2d(GL::FRAMEBUFFER, GL::COLOR_ATTACHMENT0, GL::TEXTURE_2D, Some(&tex), 0);
    gl.bind_framebuffer(GL::FRAMEBUFFER, None);
    gl.bind_texture(GL::TEXTURE_2D, None);
    (fbo, tex)
}

fn create_tileset_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let width: u32 = 80;
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

    // Tile 4: Poison swamp — sickly green with bubbles
    {
        let tx_off = 4 * 16;
        for ty in 0..16u32 {
            for tx in 0..16u32 {
                let px = tx_off + tx;
                let noise = ((tx * 7 + ty * 11) % 9) as u8;
                set_px(&mut data, px, ty, 20 + noise / 2, 50 + noise, 20 + noise / 3, 220);
            }
        }
        // Poison bubbles
        set_px(&mut data, tx_off + 4, 6, 60, 120, 40, 255);
        set_px(&mut data, tx_off + 5, 5, 60, 130, 40, 255);
        set_px(&mut data, tx_off + 10, 8, 50, 110, 35, 255);
        set_px(&mut data, tx_off + 11, 7, 55, 120, 38, 255);
        set_px(&mut data, tx_off + 7, 12, 45, 100, 30, 255);
        set_px(&mut data, tx_off + 8, 11, 50, 110, 32, 255);
        // Toxic highlights
        set_px(&mut data, tx_off + 3, 3, 80, 160, 50, 240);
        set_px(&mut data, tx_off + 12, 4, 70, 150, 45, 240);
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
        GameState::LevelUpMenu => update_level_up_menu(game),
        GameState::Victory => update_victory(game),
        _ => {}
    }
}

fn update_title_screen(game: &mut Game) {
    if game.input.consume_pressed(KeyCode::Enter) {
        if let Some(action) = game.menu.current_action() {
            match action {
                MenuAction::NewGame => {
                    game.state = GameState::Playing;
                    game.time.accumulator = 0.0;
                    game.state_timer = 0.0;
                    game.player = Player::new(1, 200.0, 200.0);
                    game.enemies = vec![
                        Enemy::new_hollow_soldier(2, 600.0, 120.0),
                        Enemy::new_archer(3, 750.0, 200.0),
                        Enemy::new_hollow_soldier(4, 650.0, 300.0),
                        Enemy::new_archer(5, 1150.0, 500.0),
                        Enemy::new_hollow_soldier(6, 1300.0, 600.0),
                        Enemy::new_knight(7, 1400.0, 650.0),
                        Enemy::new_hollow_soldier(8, 1200.0, 750.0),
                        Enemy::new_mini_boss(9, 1264.0, 1280.0),
                    ];
                    game.boss = None;
                    game.boss_active = false;
                    game.boss_defeated = false;
                    game.souls = 0;
                    game.bonfire = BonfireState::new();
                }
                MenuAction::Continue => {
                    if let Some(save) = save_manager::load_from_localstorage() {
                        game.player = Player::new(1, save.player_x, save.player_y);
                        game.player.level = save.player_level;
                        game.player.vigor = save.vigor;
                        game.player.endurance = save.endurance;
                        game.player.strength = save.strength;
                        game.player.apply_stats();
                        game.player.hp = save.player_hp;
                        // Restore weapon
                        if save.alt_weapon_name.is_some() {
                            game.player.alt_weapon = Some(crate::combat::weapon::Weapon::longsword());
                        }
                        game.souls = save.souls;
                        game.bonfire = save.bonfire.clone();
                        game.enemies_killed = save.enemies_killed;
                        game.play_time = save.play_time;
                        game.death_count = save.death_count;
                        game.boss_defeated = !save.bosses_defeated.is_empty();
                        game.enemies = vec![
                            Enemy::new_hollow_soldier(2, 620.0, 120.0),
                            Enemy::new_archer(3, 780.0, 200.0),
                            Enemy::new_hollow_soldier(4, 700.0, 320.0),
                            Enemy::new_archer(5, 1200.0, 500.0),
                            Enemy::new_hollow_soldier(6, 1350.0, 600.0),
                            Enemy::new_knight(7, 1450.0, 700.0),
                            Enemy::new_hollow_soldier(8, 1250.0, 800.0),
                            Enemy::new_mini_boss(9, 1264.0, 1280.0),
                        ];
                        game.boss = None;
                        game.boss_active = false;
                        game.camera.x = save.player_x;
                        game.camera.y = save.player_y;
                    }
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
    // Hitstop: freeze game logic for a few frames
    if game.hitstop_timer > 0.0 {
        game.hitstop_timer -= dt;
        return;
    }
    // Slow motion on boss death
    let dt = if game.slow_motion_timer > 0.0 {
        game.slow_motion_timer -= dt;
        dt * 0.2
    } else {
        dt
    };

    let mv = game.input.movement();
    let attack = game.input.pressed(KeyCode::J);
    let heavy_attack = game.input.pressed(KeyCode::K);
    let block_held = game.input.held(KeyCode::L);
    let roll = game.input.pressed(KeyCode::Space);
    let estus = game.input.consume_pressed(KeyCode::E);
    let interact = game.input.consume_pressed(KeyCode::Enter);
    let lock_on_toggle = game.input.consume_pressed(KeyCode::Tab);

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
            game.audio.play_sfx("bonfire", 0.06, 0.0);
            return;
        }
    }

    // Bloodstain soul retrieval
    if game.has_bloodstain {
        let (px, py) = game.player.position();
        let dx = px - game.bloodstain_x;
        let dy = py - game.bloodstain_y;
        let dist = (dx * dx + dy * dy).sqrt();
        if dist < 24.0 {
            game.souls += game.bloodstain_souls;
            game.has_bloodstain = false;
            game.audio.play_sfx("souls", 0.08, 0.0);
        }
    }

    // Item pickup
    let (px, py) = game.player.position();
    for item in &mut game.items {
        if item.collected { continue; }
        let dx = px - item.x;
        let dy = py - item.y;
        let dist = (dx * dx + dy * dy).sqrt();
        if dist < 20.0 {
            item.collected = true;
            match &item.kind {
                ItemKind::SoulOrb(n) => {
                    game.souls += *n;
                    game.audio.play_sfx("souls", 0.08, 0.0);
                }
                ItemKind::EstusShard => {
                    game.bonfire.estus_max += 1;
                    game.bonfire.estus_charges = game.bonfire.estus_max;
                    game.audio.play_sfx("estus", 0.1, 0.0);
                }
                ItemKind::PurpleMoss => {
                    game.player.poison_timer = 0.0;
                    game.audio.play_sfx("estus", 0.08, 0.0);
                }
                ItemKind::HomewardBone => {}
                ItemKind::WeaponDrop(wt) => {
                    use crate::combat::weapon::WeaponType;
                    let weapon = match wt {
                        WeaponType::GreatAxe => crate::combat::weapon::Weapon::great_axe(),
                        WeaponType::Dagger => crate::combat::weapon::Weapon::dagger(),
                        WeaponType::Spear => crate::combat::weapon::Weapon::spear(),
                        WeaponType::Uchigatana => crate::combat::weapon::Weapon::uchigatana(),
                        _ => crate::combat::weapon::Weapon::longsword(),
                    };
                    if game.player.alt_weapon.is_none() {
                        game.player.alt_weapon = Some(weapon);
                    } else {
                        game.player.alt_weapon = Some(weapon);
                    }
                    game.audio.play_sfx("souls", 0.08, 0.0);
                }
            }
        }
    }

    // Chest interaction
    if interact {
        for chest in &mut game.chests {
            if chest.opened { continue; }
            let dx = px - chest.x;
            let dy = py - chest.y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < 30.0 {
                chest.opened = true;
                match &chest.loot {
                    ItemKind::SoulOrb(n) => {
                        game.souls += *n;
                        game.audio.play_sfx("souls", 0.1, 0.0);
                    }
                    ItemKind::EstusShard => {
                        game.bonfire.estus_max += 1;
                        game.bonfire.estus_charges = game.bonfire.estus_max;
                        game.audio.play_sfx("estus", 0.1, 0.0);
                    }
                    ItemKind::PurpleMoss => {
                        game.player.poison_timer = 0.0;
                        game.audio.play_sfx("estus", 0.08, 0.0);
                    }
                    ItemKind::HomewardBone => {}
                    ItemKind::WeaponDrop(wt) => {
                        use crate::combat::weapon::WeaponType;
                        let weapon = match wt {
                            WeaponType::GreatAxe => crate::combat::weapon::Weapon::great_axe(),
                            WeaponType::Dagger => crate::combat::weapon::Weapon::dagger(),
                            WeaponType::Spear => crate::combat::weapon::Weapon::spear(),
                            WeaponType::Uchigatana => crate::combat::weapon::Weapon::uchigatana(),
                            _ => crate::combat::weapon::Weapon::longsword(),
                        };
                        if game.player.alt_weapon.is_none() {
                            game.player.alt_weapon = Some(weapon);
                        } else {
                            game.player.alt_weapon = Some(weapon);
                        }
                        game.audio.play_sfx("souls", 0.08, 0.0);
                    }
                }
                game.camera.add_shake(2.0);
                break;
            }
        }
    }

    // Tick state transition timer
    game.state_timer += dt;

    // Track play time
    game.play_time += dt;

    // Tick boss intro timer
    if game.boss_intro_timer > 0.0 {
        game.boss_intro_timer -= dt;
    }

    // Tick heal effect timer
    if game.heal_effect_timer > 0.0 {
        game.heal_effect_timer -= dt;
    }

    // Tick block sparks
    for spark in &mut game.block_sparks {
        spark.timer -= dt;
    }
    game.block_sparks.retain(|s| s.timer > 0.0);

    // Tick stagger bursts
    for burst in &mut game.stagger_bursts {
        burst.timer -= dt;
    }
    game.stagger_bursts.retain(|s| s.timer > 0.0);

    // Tick dust particles
    for dust in &mut game.dust_particles {
        dust.x += dust.vx * dt;
        dust.y += dust.vy * dt;
        dust.timer -= dt;
    }
    game.dust_particles.retain(|d| d.timer > 0.0);

    // Tick screen flash
    if let Some(ref mut flash) = game.screen_flash {
        flash.timer -= dt;
        if flash.timer <= 0.0 {
            game.screen_flash = None;
        }
    }

    // Tick riposte window
    if game.riposte_timer > 0.0 {
        game.riposte_timer -= dt;
    }

    // Tick damage numbers
    for dn in &mut game.damage_numbers {
        dn.y += dn.vy * dt;
        dn.vy += 30.0 * dt; // Gravity (Y-down: positive = downward pull)
        dn.timer -= dt;
    }
    game.damage_numbers.retain(|d| d.timer > 0.0);

    // Tick death particles
    for p in &mut game.death_particles {
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        p.vy += 60.0 * dt; // Gravity (Y-down: pulls downward)
        p.timer -= dt;
    }
    game.death_particles.retain(|p| p.timer > 0.0);

    // Tick level-up flash
    if game.level_up_flash > 0.0 {
        game.level_up_flash -= dt;
    }

    // Tick input buffer
    if game.input_buffer_timer > 0.0 {
        game.input_buffer_timer -= dt;
        if game.input_buffer_timer <= 0.0 {
            game.input_buffer = BufferedAction::None;
        }
    }

    // NPC dialogue interaction
    let any_npc_talking = game.npcs.iter().any(|n| n.talking);
    if any_npc_talking {
        // Advance dialogue or close
        if interact {
            for npc in &mut game.npcs {
                if npc.talking {
                    npc.dialogue_index += 1;
                    if npc.dialogue_index >= npc.dialogue.len() {
                        npc.talking = false;
                        npc.dialogue_index = 0;
                    } else if npc.dialogue_index == npc.dialogue.len() - 1 {
                        // Last line — execute NPC action
                        match npc.kind {
                            NpcKind::LevelUp => {
                                let cost = game.player.level_up_cost();
                                if game.souls >= cost as u32 {
                                    game.souls -= cost as u32;
                                    game.player.level += 1;
                                    game.player.strength += 1;
                                    game.player.apply_stats();
                                    game.level_up_flash = 0.5;
                                }
                            }
                            NpcKind::Merchant => {
                                if game.souls >= 500 {
                                    game.souls -= 500;
                                    game.bonfire.estus_max += 1;
                                    game.bonfire.estus_charges = game.bonfire.estus_max;
                                }
                            }
                            NpcKind::Blacksmith => {}
                        }
                    }
                    break;
                }
            }
        }
        if game.input.consume_pressed(KeyCode::Escape) {
            for npc in &mut game.npcs {
                npc.talking = false;
                npc.dialogue_index = 0;
            }
        }
    } else if interact {
        // Start talking to nearby NPC
        for npc in &mut game.npcs {
            let dx = px - npc.x;
            let dy = py - npc.y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < 40.0 {
                npc.talking = true;
                npc.dialogue_index = 0;
                break;
            }
        }
    }

    // Estus healing
    if estus && game.player.hp < game.player.max_hp {
        let heal = game.bonfire.use_estus();
        if heal > 0 {
            game.player.hp = (game.player.hp + heal).min(game.player.max_hp);
            game.audio.play_sfx("estus", 0.08, 0.0);
            game.heal_effect_timer = 0.8; // Show heal particles
        }
    }

    // Lock-on targeting
    if lock_on_toggle {
        let (px, py) = game.player.position();
        if game.lock_on_target.is_some() {
            game.lock_on_target = None;
        } else {
            let mut best: Option<(EntityId, f32)> = None;
            for e in &game.enemies {
                if e.is_dead() { continue; }
                let (ex, ey) = e.position();
                let d = ((px - ex) * (px - ex) + (py - ey) * (py - ey)).sqrt();
                if best.map_or(true, |(_, bd)| d < bd) {
                    best = Some((e.id(), d));
                }
            }
            if let Some((id, _)) = best {
                game.lock_on_target = Some(id);
            }
        }
    }
    // Invalidate lock-on if target died
    if let Some(tid) = game.lock_on_target {
        let still_alive = game.enemies.iter().any(|e| e.id() == tid && !e.is_dead())
            || game.boss.as_ref().map_or(false, |b| b.id() == tid && !b.is_dead());
        if !still_alive { game.lock_on_target = None; }
    }

    // Lock-on facing override: make player face the locked target
    let lock_on_pos: Option<(f32, f32)> = if let Some(tid) = game.lock_on_target {
        game.enemies.iter().find(|e| e.id() == tid).map(|e| e.position())
            .or_else(|| game.boss.as_ref().and_then(|b| if b.id() == tid { Some(b.position()) } else { None }))
    } else {
        None
    };
    if let Some((tx, ty)) = lock_on_pos {
        let (px2, py2) = game.player.position();
        game.player.facing = (ty - py2).atan2(tx - px2);
    }

    // Weapon swap (1/2 keys)
    if game.input.consume_pressed(KeyCode::Num1) {
        game.player.swap_weapon();
    }

    // Player input
    {
        // Buffer actions during stagger/attack/roll
        if attack || heavy_attack || roll {
            let can_act = matches!(game.player.state, EntityState::Idle | EntityState::Moving);
            if !can_act {
                if attack { game.input_buffer = BufferedAction::Attack; }
                else if heavy_attack { game.input_buffer = BufferedAction::HeavyAttack; }
                else if roll { game.input_buffer = BufferedAction::Roll; }
                game.input_buffer_timer = 0.5; // 500ms buffer window
            }
        }

        // Execute buffered action when player returns to idle/moving
        let buffered = game.input_buffer;
        let buffer_valid = game.input_buffer_timer > 0.0;

        let player = &mut game.player;
        match player.state {
            EntityState::Idle | EntityState::Moving => {
                if mv.0 != 0.0 || mv.1 != 0.0 {
                    // When locked on, keep facing toward target instead of movement direction
                    if game.lock_on_target.is_none() {
                        player.facing = mv.1.atan2(mv.0);
                    }
                    player.state = EntityState::Moving;
                } else {
                    player.state = EntityState::Idle;
                }
                // Execute buffered action or fresh input
                let do_attack = attack || (buffer_valid && buffered == BufferedAction::Attack);
                let do_heavy = heavy_attack || (buffer_valid && buffered == BufferedAction::HeavyAttack);
                let do_roll = roll || (buffer_valid && buffered == BufferedAction::Roll);

                if do_roll {
                    if player.stamina.consume(25.0) {
                        player.state = EntityState::Rolling;
                        player.roll_timer = player.roll_duration;
                        let (rx, ry) = player.position();
                        let roll_dir = player.facing + std::f32::consts::PI;
                        for i in 0..4 {
                            let spread = (i as f32 - 1.5) * 0.4;
                            game.dust_particles.push(DustParticle {
                                x: rx + roll_dir.cos() * 8.0,
                                y: ry + roll_dir.sin() * 8.0,
                                vx: roll_dir.cos() * 40.0 + spread * 20.0,
                                vy: roll_dir.sin() * 40.0 + spread * 20.0,
                                timer: 0.3 + i as f32 * 0.05,
                            });
                        }
                        game.input_buffer = BufferedAction::None;
                        game.input_buffer_timer = 0.0;
                    }
                }
                if do_attack {
                    let cost = player.light_stamina_cost();
                    if player.stamina.consume(cost) {
                        player.state = EntityState::Attacking;
                        player.attack_timer = player.attack_duration;
                        player.is_heavy_attack = false;
                        game.input_buffer = BufferedAction::None;
                        game.input_buffer_timer = 0.0;
                    }
                }
                if do_heavy {
                    let cost = player.heavy_stamina_cost();
                    if player.stamina.consume(cost) {
                        player.state = EntityState::Attacking;
                        player.attack_timer = player.heavy_attack_duration;
                        player.is_heavy_attack = true;
                        game.input_buffer = BufferedAction::None;
                        game.input_buffer_timer = 0.0;
                    }
                }
                if block_held {
                    player.state = EntityState::Blocking;
                    player.parry_timer = player.parry_window;
                    player.block_timer = 0.0;
                }
            }
            EntityState::Blocking => {
                if block_held {
                    player.block_timer = 0.0;
                } else {
                    player.state = EntityState::Idle;
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

    // Poison tile check
    let tile_size = TILE_SIZE as f32;
    let tx = ((rx - chunk_offset.0) / tile_size) as usize;
    let ty = ((ry - chunk_offset.1) / tile_size) as usize;
    if tx < CHUNK_SIZE && ty < CHUNK_SIZE {
        if game.chunk.tiles[ty][tx] == TileId::Poison {
            if game.player.poison_timer <= 0.0 {
                game.player.poison_timer = 8.0; // 8 seconds of poison
                game.player.poison_tick = 0.5;
            }
        }
    }

    // Enemy AI updates
    let (px, py) = game.player.position();
    for enemy in &mut game.enemies {
        if enemy.is_dead() {
            enemy.tick_death(dt);
            continue;
        }
        enemy.update_ai(px, py, dt, &game.nav_grid, chunk_offset);
        if enemy.flash_timer > 0.0 {
            enemy.flash_timer -= dt;
        }
        // Archer shooting
        if enemy.should_shoot(dt) && enemy.aggro.has_target() {
            let dx = enemy.aggro.last_known_x - enemy.transform.x;
            let dy = enemy.aggro.last_known_y - enemy.transform.y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist > 1.0 {
                let speed = 200.0;
                game.projectiles.push(Projectile {
                    x: enemy.transform.x,
                    y: enemy.transform.y,
                    vx: dx / dist * speed,
                    vy: dy / dist * speed,
                    damage: enemy.damage,
                    timer: 2.0,
                });
            }
        }
        // Resolve enemy collision with walls
        let (ex, ey) = enemy.position();
        let (rx, ry) = game.collision.resolve_aabb(chunk_offset, ex, ey, 14.0, 14.0);
        enemy.set_position(rx, ry);
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
    let is_heavy = game.player.is_heavy_attack;
    let attack_range = if is_heavy { 56.0 } else { 40.0 };
    let attack_damage = if is_heavy { game.player.damage() * 2 } else { game.player.damage() };
    let attack_knockback = if is_heavy { 12.0 } else { 6.0 };

    for enemy in &mut game.enemies {
        if enemy.is_dead() {
            continue;
        }
        let (ex, ey) = enemy.position();
        let dist = ((px - ex) * (px - ex) + (py - ey) * (py - ey)).sqrt();

        if player_attacking && dist < attack_range {
            // Knight blocking — reduce damage
            let blocked = enemy.try_block();
            let final_damage = if blocked {
                (attack_damage as f32 * 0.3) as i32
            } else {
                attack_damage
            };
            let dmg = DamageInfo {
                damage: final_damage,
                knockback_x: 0.0,
                knockback_y: 0.0,
                poise_damage: if is_heavy { 40.0 } else { 20.0 },
                attacker_id: game.player.id(),
            };
            // Check for riposte (enemy is staggered and this is a follow-up attack)
            let is_riposte = game.riposte_timer > 0.0 && game.riposte_target_id == enemy.id()
                && *enemy.state() == EntityState::Staggered;
            let riposte_multiplier = if is_riposte { 3.0 } else { 1.0 };

            let actual_damage = (final_damage as f32 * riposte_multiplier) as i32;
            let dmg = DamageInfo {
                damage: actual_damage,
                knockback_x: 0.0,
                knockback_y: 0.0,
                poise_damage: if is_heavy { 40.0 } else { 20.0 },
                attacker_id: game.player.id(),
            };
            enemy.take_damage(&dmg);
            game.camera.add_shake(if is_riposte { 10.0 } else if is_heavy { 6.0 } else { 3.0 });
            // Hitstop on hit
            game.hitstop_timer = if is_heavy { 0.05 } else { 0.02 };
            game.audio.play_sfx(if is_riposte { "hit" } else { "hit" }, if is_riposte { 0.2 } else { 0.12 }, 0.0);
            // Damage number
            game.damage_numbers.push(DamageNumber {
                x: ex + ((game.damage_numbers.len() as f32 % 5.0) - 2.0) * 4.0,
                y: ey - 24.0,
                vy: -40.0,
                value: if blocked { (attack_damage as f32 * 0.3) as i32 } else { actual_damage },
                timer: 0.8,
                is_player_damage: false,
            });
            game.damage_dealt += if blocked { (attack_damage as f32 * 0.3) as u32 } else { actual_damage as u32 };
            // Stagger burst on hit
            if !blocked {
                game.stagger_bursts.push(BlockSpark { x: ex, y: ey, timer: 0.2 });
            }
            // Knight block spark
            if blocked {
                game.block_sparks.push(BlockSpark { x: ex, y: ey, timer: 0.3 });
            }
            // Clear riposte after use
            if is_riposte {
                game.riposte_timer = 0.0;
                game.riposte_target_id = 0;
                game.screen_flash = Some(ScreenFlash { timer: 0.15, max_timer: 0.15, color: [1.0, 0.9, 0.3, 0.3] });
            }
            if enemy.is_dead() {
                game.enemies_killed += 1;
                let soul_reward = match enemy.kind {
                    crate::entity::enemy::EnemyKind::HollowSoldier => 100,
                    crate::entity::enemy::EnemyKind::Archer => 150,
                    crate::entity::enemy::EnemyKind::Knight => 200,
                };
                game.souls += soul_reward;
                game.camera.add_shake(6.0);
                game.audio.play_sfx("enemy_die", 0.1, 0.0);
                // Spawn death dissolve particles
                let (ex, ey) = enemy.position();
                for i in 0..12 {
                    let angle = (i as f32 / 12.0) * std::f32::consts::TAU;
                    let speed = 40.0 + (i as f32 % 4.0) * 15.0;
                    game.death_particles.push(DeathParticle {
                        x: ex + (i as f32 % 3.0 - 1.0) * 6.0,
                        y: ey + (i as f32 % 3.0 - 1.0) * 6.0,
                        vx: angle.cos() * speed,
                        vy: -(angle.sin() * speed) + 30.0,
                        timer: 0.4 + (i as f32 % 4.0) * 0.1,
                        size: 4.0 + (i as f32 % 3.0) * 2.0,
                    });
                }
                // Spawn soul orbs
                for _ in 0..5 {
                    game.soul_orbs.push(SoulOrb {
                        x: ex + (game.soul_orbs.len() as f32 % 3.0 - 1.0) * 6.0,
                        y: ey,
                        vy: -(30.0 + (game.soul_orbs.len() as f32 % 5.0) * 8.0),
                        timer: 0.6 + (game.soul_orbs.len() as f32 % 3.0) * 0.2,
                        max_time: 0.6 + (game.soul_orbs.len() as f32 % 3.0) * 0.2,
                    });
                }
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

                // Parry — stagger enemy
                if game.player.is_parrying() {
                    enemy.fsm.current_state = STAGGERED;
                    enemy.fsm.state_timer = 0.0;
                    enemy.state = EntityState::Staggered;
                    game.riposte_timer = 1.5; // Window to riposte
                    game.riposte_target_id = enemy.id();
                    game.screen_flash = Some(ScreenFlash { timer: 0.12, max_timer: 0.12, color: [0.2, 1.0, 1.0, 0.4] });
                    game.stagger_bursts.push(BlockSpark { x: (px + ex) * 0.5, y: (py + ey) * 0.5, timer: 0.3 });
                    game.audio.play_sfx("hit", 0.15, 0.0);
                } else if *game.player.state() == EntityState::Blocking {
                    game.damage_taken += (enemy.damage as f32 * 0.3) as u32;
                    game.audio.play_sfx("hit", 0.08, 0.0);
                } else {
                    game.camera.add_shake(8.0);
                    game.audio.play_sfx("player_hit", 0.15, 0.0);
                    game.damage_taken += enemy.damage as u32;
                    // Damage number on player
                    game.damage_numbers.push(DamageNumber {
                        x: px,
                        y: py - 24.0,
                        vy: -50.0,
                        value: enemy.damage,
                        timer: 0.8,
                        is_player_damage: true,
                    });
                }
                enemy.has_hit_this_attack = true;
            }
        }
    }

    // --- Combat: player vs boss ---
    if let Some(ref mut boss) = game.boss {
        let (bx, by) = boss.position();
        let dist = ((px - bx) * (px - bx) + (py - by) * (py - by)).sqrt();

        if player_attacking && dist < attack_range + 16.0 {
            let dmg = DamageInfo {
                damage: if is_heavy { attack_damage * 2 } else { game.player.damage() * 2 },
                knockback_x: 0.0,
                knockback_y: 0.0,
                poise_damage: if is_heavy { 40.0 } else { 20.0 },
                attacker_id: game.player.id(),
            };
            boss.take_damage(&dmg);
            game.camera.add_shake(if is_heavy { 8.0 } else { 4.0 });
            game.audio.play_sfx("hit", 0.12, 0.0);
            if boss.is_dead() && !game.boss_defeated {
                game.boss_defeated = true;
                game.souls += 5000;
                game.camera.add_shake(15.0);
                game.slow_motion_timer = 1.5; // Slow-mo for 1.5s on boss death
                game.audio.play_sfx("boss_die", 0.2, 0.0);
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

                if game.player.is_parrying() {
                    boss.state = EntityState::Staggered;
                    boss.stagger_timer = 0.5;
                    game.audio.play_sfx("hit", 0.18, 0.0);
                } else if *game.player.state() == EntityState::Blocking {
                    game.audio.play_sfx("hit", 0.1, 0.0);
                } else {
                    game.camera.add_shake(12.0);
                    game.audio.play_sfx("player_hit", 0.18, 0.0);
                }
                boss.has_hit_this_attack = true;
            }
        }
    }

    // --- Spawn boss when mini-boss (last enemy) is killed ---
    if !game.boss_active && !game.boss_defeated && game.enemies.last().map_or(false, |e| e.is_dead()) {
        // Spawn random boss variety
        let boss_type = (game.enemies_killed * 1103515245 + 12345) as usize % 3;
        game.boss = Some(match boss_type {
            0 => Boss::new_test_boss(10, 1750.0, 400.0),
            1 => Boss::new_dragonrider(10, 1750.0, 400.0),
            _ => Boss::new_ruin_sentinel(10, 1750.0, 400.0),
        });
        game.boss_active = true;
        game.boss_intro_timer = 3.0; // Show boss name for 3 seconds
    }

    // --- Update soul orbs ---
    for orb in &mut game.soul_orbs {
        orb.y += orb.vy * dt;
        orb.timer -= dt;
    }
    game.soul_orbs.retain(|orb| orb.timer > 0.0);

    // --- Update projectiles ---
    let (px, py) = game.player.position();
    for proj in &mut game.projectiles {
        proj.x += proj.vx * dt;
        proj.y += proj.vy * dt;
        proj.timer -= dt;

        // Check collision with player
        if *game.player.state() != EntityState::Rolling {
            let dx = px - proj.x;
            let dy = py - proj.y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < 18.0 {
                let dmg = DamageInfo {
                    damage: proj.damage,
                    knockback_x: 0.0, knockback_y: 0.0,
                    poise_damage: 5.0,
                    attacker_id: 99,
                };
                game.player.take_damage(&dmg);
                if !game.player.is_parrying() && *game.player.state() != EntityState::Blocking {
                    game.camera.add_shake(4.0);
                    game.audio.play_sfx("player_hit", 0.1, 0.0);
                }
                proj.timer = 0.0;
            }
        }
    }
    game.projectiles.retain(|p| p.timer > 0.0);

    // --- Update lights — player torch follows player ---
    if !game.lights.is_empty() {
        game.lights[0].x = px;
        game.lights[0].y = py;
    }

    // Camera follows player (or midpoint between player and lock-on target)
    if let Some((tx, ty)) = lock_on_pos {
        let mid_x = (px + tx) * 0.5;
        let mid_y = (py + ty) * 0.5;
        game.camera.follow(mid_x, mid_y, 4.0, dt);
    } else {
        game.camera.follow(px, py, 5.0, dt);
    }
    game.camera.update(dt);

    // Audio listener position
    game.audio.set_listener_position(px, py);

    // Combat music — start when enemies are aggro'd
    let any_aggro = game.enemies.iter().any(|e| !e.is_dead() && e.aggro.has_target());
    let boss_aggro = game.boss.as_ref().map_or(false, |b| !b.is_dead() && b.aggro.has_target());
    game.audio.set_combat_music(any_aggro || boss_aggro);

    // Check victory
    if game.boss_defeated {
        if let Some(ref boss) = game.boss {
            if boss.is_dead() {
                game.state = GameState::Victory;
                game.audio.play_sfx("victory", 0.12, 0.0);
            }
        }
    }

    // Check player death
    if game.player.is_dead() {
        // Drop bloodstain with souls
        if game.souls > 0 {
            let (dx, dy) = game.player.position();
            game.bloodstain_x = dx;
            game.bloodstain_y = dy;
            game.bloodstain_souls = game.souls;
            game.has_bloodstain = true;
        }
        game.souls = 0;
        game.death_count += 1;
        game.death_anim_timer = 0.0; // Start death animation
        game.audio.set_combat_music(false);
        game.state = GameState::DeathScreen;
        game.menu = MenuState::death_screen();
        game.audio.play_sfx("death", 0.15, 0.0);
    }
}

fn update_death(game: &mut Game) {
    game.death_anim_timer += FIXED_DT as f32;
    // Only allow input after death animation completes (2.5s)
    if game.death_anim_timer < 2.5 {
        return;
    }
    if game.input.consume_pressed(KeyCode::Enter) {
        if let Some(action) = game.menu.current_action() {
            match action {
                MenuAction::Continue => {
                    // Respawn at bonfire
                    game.player = Player::new(1, 200.0, 200.0);
                    game.souls = 0;
                    game.bonfire.rest();
                    game.bonfire.estus_charges = game.bonfire.estus_max;
                    game.enemies = vec![
                        Enemy::new_hollow_soldier(2, 600.0, 120.0),
                        Enemy::new_archer(3, 750.0, 200.0),
                        Enemy::new_hollow_soldier(4, 650.0, 300.0),
                        Enemy::new_archer(5, 1150.0, 500.0),
                        Enemy::new_hollow_soldier(6, 1300.0, 600.0),
                        Enemy::new_knight(7, 1400.0, 650.0),
                        Enemy::new_hollow_soldier(8, 1200.0, 750.0),
                        Enemy::new_mini_boss(9, 1264.0, 1280.0),
                    ];
                    game.boss = None;
                    game.boss_active = false;
                    game.boss_defeated = false;
                    game.projectiles.clear();
                    game.time.accumulator = 0.0;
                    game.state_timer = 0.0;
                    game.death_anim_timer = 0.0;
                    game.state = GameState::Playing;
                }
                MenuAction::QuitToTitle => {
                    game.state = GameState::TitleScreen;
                    game.menu = MenuState::title_screen_with_save_check();
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
    if game.input.consume_pressed(KeyCode::Escape) {
        game.state = GameState::Playing;
        return;
    }
    if game.input.consume_pressed(KeyCode::Enter) {
        if let Some(action) = game.menu.current_action().cloned() {
            match action {
                MenuAction::Rest => {
                    game.bonfire.rest();
                    game.player.hp = game.player.max_hp;
                    game.bonfire.estus_charges = game.bonfire.estus_max;
                    game.player.stamina.current = game.player.stamina.maximum;
                    // Respawn enemies (reset to initial spawns)
                    game.enemies = vec![
                        Enemy::new_hollow_soldier(2, 620.0, 120.0),
                        Enemy::new_archer(3, 780.0, 200.0),
                        Enemy::new_hollow_soldier(4, 700.0, 320.0),
                        Enemy::new_archer(5, 1200.0, 500.0),
                        Enemy::new_hollow_soldier(6, 1350.0, 600.0),
                        Enemy::new_knight(7, 1450.0, 700.0),
                        Enemy::new_hollow_soldier(8, 1250.0, 800.0),
                        Enemy::new_mini_boss(9, 1264.0, 1280.0),
                    ];
                    game.boss = None;
                    game.boss_active = false;
                    game.boss_defeated = false;
                    game.projectiles.clear();
                    // Auto-save at bonfire
                    let (px, py) = game.player.position();
                    let save = SaveData {
                        player_level: game.player.level,
                        vigor: game.player.vigor,
                        endurance: game.player.endurance,
                        strength: game.player.strength,
                        souls: game.souls,
                        bonfire: game.bonfire.clone(),
                        current_room: "dungeon".into(),
                        player_hp: game.player.hp,
                        player_x: px,
                        player_y: py,
                        weapon_name: game.player.weapon.name.clone(),
                        alt_weapon_name: game.player.alt_weapon.as_ref().map(|w| w.name.clone()),
                        bosses_defeated: if game.boss_defeated { vec!["boss1".into()] } else { vec![] },
                        enemies_killed: game.enemies_killed,
                        items_collected: game.items.iter().filter(|i| i.collected).map(|_| "item".into()).collect(),
                        chests_opened: game.chests.iter().filter(|c| c.opened).map(|_| "chest".into()).collect(),
                        play_time: game.play_time,
                        death_count: game.death_count,
                    };
                    save_manager::save_to_localstorage(&save);
                }
                MenuAction::LevelUp => {
                    game.state = GameState::LevelUpMenu;
                    game.menu = MenuState::level_up_menu();
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

fn update_level_up_menu(game: &mut Game) {
    if game.input.consume_pressed(KeyCode::Escape) {
        game.state = GameState::BonfireMenu;
        game.menu = MenuState::bonfire_menu();
        return;
    }
    if game.input.consume_pressed(KeyCode::Enter) {
        let cost = game.player.level_up_cost();
        if game.souls >= cost {
            let idx = game.menu.selected_index;
            match idx {
                0 => { game.player.vigor += 1; game.souls -= cost; game.player.level += 1; game.player.apply_stats(); game.player.hp = game.player.max_hp; game.level_up_flash = 1.5; }
                1 => { game.player.endurance += 1; game.souls -= cost; game.player.level += 1; game.player.apply_stats(); game.level_up_flash = 1.5; }
                2 => { game.player.strength += 1; game.souls -= cost; game.player.level += 1; game.player.apply_stats(); game.level_up_flash = 1.5; }
                3 => { game.state = GameState::BonfireMenu; game.menu = MenuState::bonfire_menu(); }
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
    if game.input.consume_pressed(KeyCode::Enter) {
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
    use web_sys::WebGl2RenderingContext as GL;

    // --- Pass 1: Render scene to FBO ---
    gl.bind_framebuffer(GL::FRAMEBUFFER, Some(&game.scene_fbo));
    gl.viewport(0, 0, game.screen_w as i32, game.screen_h as i32);
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
        // Warm glow aura (pulsing)
        let pulse = ((game.time.accumulator as f32 * 1.5).sin() * 0.15 + 0.85);
        game.batcher.draw(
            InstanceData::new(game.bonfire_x, game.bonfire_y, 64.0 * pulse, 64.0 * pulse, [0.0, 0.0, 1.0, 1.0], [0.9, 0.6, 0.1, 0.12]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(game.bonfire_x, game.bonfire_y, 48.0 * pulse, 48.0 * pulse, [0.0, 0.0, 1.0, 1.0], [1.0, 0.7, 0.2, 0.15]),
            &game.white_tex, gl,
        );
        let bonfire_data = InstanceData::new(
            game.bonfire_x, game.bonfire_y,
            32.0, 32.0,
            [0.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
        );
        game.batcher.draw(bonfire_data, &game.bonfire_tex, gl);
    }

    // --- Draw wall torches (at light positions, skip player light [0] and bonfire light [1]) ---
    for i in 2..game.lights.len() {
        let light = &game.lights[i];
        let flicker = ((game.time.accumulator as f32 * (3.0 + i as f32 * 0.7)).sin() * 0.2 + 0.8);
        // Torch bracket (brown)
        game.batcher.draw(
            InstanceData::new(light.x, light.y - 6.0, 6.0, 8.0, [0.0, 0.0, 1.0, 1.0], [0.5, 0.35, 0.2, 1.0]),
            &game.white_tex, gl,
        );
        // Flame (orange flickering)
        game.batcher.draw(
            InstanceData::new(light.x, light.y - 12.0, 5.0 * flicker, 6.0 * flicker, [0.0, 0.0, 1.0, 1.0], [1.0, 0.6, 0.1, 0.9]),
            &game.white_tex, gl,
        );
    }

    // --- Draw world items ---
    for item in &game.items {
        if item.collected { continue; }
        let (r, g, b) = match &item.kind {
            ItemKind::SoulOrb(_) => (0.6, 0.8, 1.0),
            ItemKind::EstusShard => (0.2, 0.9, 0.3),
            ItemKind::HomewardBone => (0.8, 0.7, 0.5),
            ItemKind::PurpleMoss => (0.6, 0.2, 0.8),
            ItemKind::WeaponDrop(_) => (0.9, 0.6, 0.1),
        };
        let bob = (item.y * 0.05).sin() * 3.0;
        game.batcher.draw(
            InstanceData::new(item.x, item.y + bob, 12.0, 12.0, [0.0, 0.0, 1.0, 1.0], [r, g, b, 0.9]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(item.x, item.y + bob, 20.0, 20.0, [0.0, 0.0, 1.0, 1.0], [r, g, b, 0.2]),
            &game.white_tex, gl,
        );
    }

    // --- Draw treasure chests ---
    for chest in &game.chests {
        let (color, size) = if chest.opened {
            ([0.4, 0.35, 0.25, 0.6], 16.0) // Dim when opened
        } else {
            ([0.8, 0.65, 0.2, 1.0], 20.0) // Golden when closed
        };
        // Chest body
        game.batcher.draw(
            InstanceData::new(chest.x, chest.y, size, size * 0.7, [0.0, 0.0, 1.0, 1.0], color),
            &game.white_tex, gl,
        );
        if !chest.opened {
            // Lock/clasp
            game.batcher.draw(
                InstanceData::new(chest.x, chest.y - 2.0, 6.0, 4.0, [0.0, 0.0, 1.0, 1.0], [0.9, 0.8, 0.3, 1.0]),
                &game.white_tex, gl,
            );
            // Glow
            game.batcher.draw(
                InstanceData::new(chest.x, chest.y, size + 10.0, size + 10.0, [0.0, 0.0, 1.0, 1.0], [0.8, 0.6, 0.1, 0.15]),
                &game.white_tex, gl,
            );
        }
    }

    // --- Draw bloodstain ---
    if game.has_bloodstain {
        let pulse = ((game.time.accumulator as f32).sin() * 0.3 + 0.7);
        // Glow
        game.batcher.draw(
            InstanceData::new(game.bloodstain_x, game.bloodstain_y, 32.0 * pulse, 32.0 * pulse, [0.0, 0.0, 1.0, 1.0], [0.8, 0.1, 0.1, 0.2 * pulse]),
            &game.white_tex, gl,
        );
        let bloodstain_data = InstanceData::new(
            game.bloodstain_x, game.bloodstain_y,
            16.0, 16.0,
            [0.0, 0.0, 1.0, 1.0],
            [0.9, 0.15, 0.15, 0.8],
        );
        game.batcher.draw(bloodstain_data, &game.white_tex, gl);
    }

    // --- Draw NPCs ---
    for npc in &game.npcs {
        let bob = (game.play_time * 2.0).sin() * 2.0;
        game.batcher.draw(
            InstanceData::new(npc.x, npc.y + bob, 28.0, 28.0, [0.0, 0.0, 1.0, 1.0], npc.color),
            &game.white_tex, gl,
        );
        // Name above NPC
        let proximity = {
            let dx = game.player.transform.x - npc.x;
            let dy = game.player.transform.y - npc.y;
            (dx * dx + dy * dy).sqrt() < 50.0
        };
        if proximity {
            game.batcher.draw(
                InstanceData::new(npc.x, npc.y - 24.0, 6.0, 6.0, [0.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.0, 0.8]),
                &game.white_tex, gl,
            );
        }
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

    // --- Lock-on indicator ---
    if let Some(tid) = game.lock_on_target {
        let target_pos = game.enemies.iter().find(|e| e.id() == tid).map(|e| e.position())
            .or_else(|| game.boss.as_ref().and_then(|b| if b.id() == tid { Some(b.position()) } else { None }));
        if let Some((tx, ty)) = target_pos {
            let pulse = 0.7 + 0.3 * (game.play_time * 4.0).sin();
            let indicator_y = ty - 26.0;
            // Outer ring — 8 dots in a circle
            for i in 0..8 {
                let a = (i as f32 / 8.0) * std::f32::consts::TAU + game.play_time * 2.0;
                let r = 12.0;
                let dx = a.cos() * r;
                let dy = a.sin() * r;
                game.batcher.draw(
                    InstanceData::new(tx + dx, indicator_y + dy, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0],
                        [1.0, 0.85, 0.1, 0.8 * pulse]),
                    &game.white_tex, gl,
                );
            }
            // Inner diamond — 4 dots
            for i in 0..4 {
                let a = (i as f32 / 4.0) * std::f32::consts::TAU;
                let r = 5.0;
                let dx = a.cos() * r;
                let dy = a.sin() * r;
                game.batcher.draw(
                    InstanceData::new(tx + dx, indicator_y + dy, 3.0, 3.0, [0.0, 0.0, 1.0, 1.0],
                        [1.0, 0.9, 0.2, 0.9]),
                    &game.white_tex, gl,
                );
            }
            // Center bright dot
            game.batcher.draw(
                InstanceData::new(tx, indicator_y, 3.0, 3.0, [0.0, 0.0, 1.0, 1.0],
                    [1.0, 1.0, 0.5, 1.0]),
                &game.white_tex, gl,
            );
        }
    }

    // --- Draw projectiles (arrows) ---
    for proj in &game.projectiles {
        game.batcher.draw(
            InstanceData::new(proj.x, proj.y, 8.0, 3.0, [0.0, 0.0, 1.0, 1.0], [0.8, 0.6, 0.2, 1.0]),
            &game.white_tex, gl,
        );
    }

    // --- Draw block sparks (when knight blocks) ---
    for spark in &game.block_sparks {
        let alpha = spark.timer / 0.3;
        // Shield spark - blue/white flash
        for i in 0..4 {
            let angle = (i as f32 / 4.0) * std::f32::consts::TAU + spark.timer * 10.0;
            let r = 12.0 * (1.0 - alpha);
            let ox = spark.x + angle.cos() * r;
            let oy = spark.y + angle.sin() * r;
            game.batcher.draw(
                InstanceData::new(ox, oy, 8.0, 8.0, [0.0, 0.0, 1.0, 1.0], [0.5, 0.7, 1.0, alpha]),
                &game.white_tex, gl,
            );
        }
        // Center flash
        game.batcher.draw(
            InstanceData::new(spark.x, spark.y, 20.0, 20.0, [0.0, 0.0, 1.0, 1.0], [0.3, 0.5, 1.0, alpha * 0.4]),
            &game.white_tex, gl,
        );
    }

    // --- Draw stagger bursts (yellow ring on hit) ---
    for burst in &game.stagger_bursts {
        let alpha = burst.timer / 0.2;
        let size = 24.0 * (1.0 - alpha) + 8.0;
        game.batcher.draw(
            InstanceData::new(burst.x, burst.y, size, size, [0.0, 0.0, 1.0, 1.0], [1.0, 0.9, 0.3, alpha * 0.5]),
            &game.white_tex, gl,
        );
    }

    // --- Draw dust particles (from rolls) ---
    for dust in &game.dust_particles {
        let alpha = dust.timer / 0.4;
        game.batcher.draw(
            InstanceData::new(dust.x, dust.y, 6.0, 6.0, [0.0, 0.0, 1.0, 1.0], [0.7, 0.65, 0.5, alpha * 0.6]),
            &game.white_tex, gl,
        );
    }

    // --- Draw damage numbers ---
    for dn in &game.damage_numbers {
        let alpha = (dn.timer / 0.8).min(1.0);
        let color: [f32; 4] = if dn.is_player_damage {
            [1.0, 0.3, 0.3, alpha]
        } else {
            [1.0, 1.0, 0.5, alpha]
        };
        let size = 6.0 + (dn.value as f32 / 20.0).min(8.0);
        game.batcher.draw(
            InstanceData::new(dn.x, dn.y, size + 2.0, size + 2.0, [0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 0.0, alpha * 0.5]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(dn.x, dn.y, size, size, [0.0, 0.0, 1.0, 1.0], color),
            &game.white_tex, gl,
        );
    }

    // --- Draw death dissolve particles ---
    for p in &game.death_particles {
        let alpha = (p.timer / 0.7).min(1.0);
        game.batcher.draw(
            InstanceData::new(p.x, p.y, p.size, p.size, [0.0, 0.0, 1.0, 1.0], [0.4, 0.3, 0.2, alpha * 0.8]),
            &game.white_tex, gl,
        );
    }

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

    // --- Draw soul orbs ---
    for orb in &game.soul_orbs {
        let alpha = (orb.timer / orb.max_time).min(1.0);
        game.batcher.draw(
            InstanceData::new(orb.x, orb.y, 8.0, 8.0, [0.0, 0.0, 1.0, 1.0], [0.6, 0.8, 1.0, alpha]),
            &game.white_tex, gl,
        );
    }

    // --- Draw player ---
    game.player.render(&mut game.batcher, &game.player_tex, gl);

    // --- Heal effect (green particles around player) ---
    if game.heal_effect_timer > 0.0 {
        let (px, py) = game.player.position();
        let t = game.heal_effect_timer;
        let alpha = t / 0.8;
        for i in 0..6 {
            let angle = (i as f32 / 6.0) * std::f32::consts::TAU + t * 4.0;
            let radius = 20.0 * (1.0 - alpha);
            let ox = px + angle.cos() * radius;
            let oy = py + angle.sin() * radius;
            game.batcher.draw(
                InstanceData::new(ox, oy, 6.0, 6.0, [0.0, 0.0, 1.0, 1.0], [0.2, 0.9, 0.3, alpha * 0.8]),
                &game.white_tex, gl,
            );
        }
        // Healing ring
        game.batcher.draw(
            InstanceData::new(px, py, 40.0 * (1.0 + (1.0 - alpha) * 0.5), 40.0 * (1.0 + (1.0 - alpha) * 0.5), [0.0, 0.0, 1.0, 1.0], [0.3, 1.0, 0.4, alpha * 0.3]),
            &game.white_tex, gl,
        );
    }

    // --- Draw attack swing effect (arc trail) ---
    if *game.player.state() == EntityState::Attacking {
        let (px, py) = game.player.position();
        let facing = game.player.facing;
        let t = game.player.attack_timer;
        let total = if game.player.is_heavy_attack { game.player.heavy_attack_duration } else { game.player.attack_duration };
        let progress = 1.0 - (t / total);
        let range = if game.player.is_heavy_attack { 36.0 } else { 28.0 };
        let arc_span = if game.player.is_heavy_attack { 1.2 } else { 0.8 }; // radians

        // Draw arc of small rectangles
        let steps = if game.player.is_heavy_attack { 8 } else { 5 };
        for i in 0..steps {
            let frac = i as f32 / steps as f32;
            let arc_t = (frac + progress * 0.3).min(1.0);
            let angle = facing - arc_span * 0.5 + arc_span * arc_t;
            let dist = range * (0.6 + frac * 0.4);
            let sx = px + angle.cos() * dist;
            let sy = py + angle.sin() * dist;
            let alpha = (1.0 - frac) * 0.6 * (1.0 - progress * 0.5);
            let size = if game.player.is_heavy_attack { 10.0 - frac * 4.0 } else { 7.0 - frac * 3.0 };
            let color: [f32; 4] = if game.player.is_heavy_attack {
                [1.0, 0.6 + frac * 0.2, 0.1, alpha]
            } else {
                [1.0, 0.9, 0.5, alpha]
            };
            game.batcher.draw(
                InstanceData::new(sx, sy, size, size * 0.4, [0.0, 0.0, 1.0, 1.0], color),
                &game.white_tex, gl,
            );
        }

        // Impact point
        if progress > 0.3 && progress < 0.7 {
            let sx = px + facing.cos() * range;
            let sy = py + facing.sin() * range;
            let alpha = 0.4 * (1.0 - (progress - 0.3) / 0.4);
            game.batcher.draw(
                InstanceData::new(sx, sy, 16.0, 16.0, [0.0, 0.0, 1.0, 1.0], [1.0, 1.0, 1.0, alpha]),
                &game.white_tex, gl,
            );
        }
    }

    game.batcher.flush(gl);

    // --- Pass 2: Post-processing composite to screen ---
    gl.bind_framebuffer(GL::FRAMEBUFFER, None);
    gl.viewport(0, 0, game.screen_w as i32, game.screen_h as i32);
    gl.clear_color(0.0, 0.0, 0.0, 1.0);
    gl.clear(GL::COLOR_BUFFER_BIT);

    // Bind scene texture and run composite shader
    gl.active_texture(GL::TEXTURE0);
    gl.bind_texture(GL::TEXTURE_2D, Some(&game.scene_texture));
    // Low HP warning: redder tint
    let hp_ratio = game.player.hp as f32 / game.player.max_hp as f32;
    let (brightness, saturation, fog_color) = if hp_ratio < 0.25 {
        (0.9, 0.6, [0.08, 0.02, 0.02, 0.7]) // Red tint when low HP
    } else {
        (1.0, 0.85, [0.02, 0.02, 0.04, 0.6])
    };
    game.post_processor.render(
        gl,
        1.2,                                               // vignette intensity
        fog_color,                                          // fog color + alpha
        [game.screen_h * 0.3, game.screen_h * 0.7],       // fog distance range
        brightness,                                         // brightness
        saturation,                                         // saturation
    );

    // --- HUD projection (used by vignette + HUD elements) ---
    let ui_proj = UiRenderer::screen_projection(game.screen_w, game.screen_h);

    // --- Screen flash (parry, riposte) ---
    if let Some(ref flash) = game.screen_flash {
        let alpha = flash.timer / flash.max_timer;
        let c = flash.color;
        game.ui_renderer.draw_bar(
            gl, game.screen_w * 0.5, game.screen_h * 0.5,
            game.screen_w, game.screen_h,
            1.0,
            [c[0], c[1], c[2], c[3] * alpha],
            [c[0], c[1], c[2], c[3] * alpha],
            &ui_proj,
        );
    }

    // --- Poison overlay ---
    if game.player.poison_timer > 0.0 {
        let pulse = ((game.time.accumulator as f32 * 2.0).sin() * 0.1 + 0.15);
        game.ui_renderer.draw_bar(
            gl, game.screen_w * 0.5, game.screen_h * 0.5,
            game.screen_w, game.screen_h,
            1.0,
            [0.0, 0.3, 0.0, pulse],
            [0.0, 0.3, 0.0, pulse],
            &ui_proj,
        );
    }

    // --- HUD (screen-space) ---

    // HP bar (x,y = center of bar)
    let hp_ratio = game.player.hp as f32 / game.player.max_hp as f32;
    let hp_bar_w = 200.0;
    let hp_bar_h = 16.0;
    let hp_bar_x = 20.0 + hp_bar_w * 0.5; // left edge at x=20
    game.ui_renderer.draw_bar(
        gl, hp_bar_x, 20.0, hp_bar_w, hp_bar_h,
        hp_ratio,
        [0.15, 0.15, 0.15, 0.8],
        [0.7, 0.1, 0.1, 0.9],
        &ui_proj,
    );

    // Stamina bar
    let stamina_ratio = game.player.stamina.current / game.player.stamina.maximum;
    let sta_bar_w = 200.0;
    let sta_bar_h = 12.0;
    let sta_bar_x = 20.0 + sta_bar_w * 0.5;
    game.ui_renderer.draw_bar(
        gl, sta_bar_x, 42.0, sta_bar_w, sta_bar_h,
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
            let boss_bar_x = game.screen_w * 0.5; // center of screen
            game.ui_renderer.draw_bar(
                gl, boss_bar_x, 20.0, boss_bar_w, 14.0,
                boss_hp_ratio,
                [0.15, 0.15, 0.15, 0.8],
                [0.8, 0.2, 0.8, 0.9],
                &ui_proj,
            );
        }
    }

    // Estus indicator — show individual flask charges as small squares
    {
        let flask_size = 10.0;
        let flask_gap = 3.0;
        let start_x = 20.0;
        let flask_y = 58.0;
        for i in 0..game.bonfire.estus_max {
            let x = start_x + flask_size * 0.5 + i as f32 * (flask_size + flask_gap);
            let filled = i < game.bonfire.estus_charges;
            let color: [f32; 4] = if filled {
                [0.9, 0.7, 0.1, 0.9] // Gold for available
            } else {
                [0.2, 0.2, 0.2, 0.6] // Dark grey for used
            };
            game.ui_renderer.draw_bar(
                gl, x, flask_y, flask_size, flask_size,
                1.0, color, color, &ui_proj,
            );
        }
    }

    // --- Mini-map (top-right corner) ---
    {
        let map_size = 150.0;
        let map_left = game.screen_w - map_size - 10.0;
        let map_top = 10.0;
        let map_cx = map_left + map_size * 0.5;
        let map_cy = map_top + map_size * 0.5;
        let world_size = CHUNK_SIZE as f32 * TILE_SIZE as f32;
        let scale = map_size / world_size;

        // Background
        game.ui_renderer.draw_bar(
            gl, map_cx, map_cy, map_size + 4.0, map_size + 4.0,
            1.0, [0.0, 0.0, 0.0, 0.7], [0.0, 0.0, 0.0, 0.7], &ui_proj,
        );

        // Draw each tile as a tiny rectangle (sample every 4 tiles)
        let step = 4;
        for ty in (0..CHUNK_SIZE).step_by(step) {
            for tx in (0..CHUNK_SIZE).step_by(step) {
                let tile = game.chunk.tiles[ty][tx];
                if tile == TileId::Empty { continue; }
                let is_wall = tile == TileId::Wall;
                let color: [f32; 4] = if is_wall {
                    [0.25, 0.22, 0.2, 0.9]
                } else {
                    [0.55, 0.48, 0.35, 1.0]
                };
                // Tile world position → map pixel position
                let dot_x = map_left + (tx as f32 * TILE_SIZE as f32) * scale;
                let dot_y = map_top + (ty as f32 * TILE_SIZE as f32) * scale;
                let s = step as f32 * TILE_SIZE as f32 * scale;
                game.ui_renderer.draw_bar(
                    gl, dot_x + s * 0.5, dot_y + s * 0.5, s, s,
                    1.0, color, color, &ui_proj,
                );
            }
        }

        // Player dot (cyan)
        let (ppx, ppy) = game.player.position();
        let pdx = map_left + ppx * scale;
        let pdy = map_top + ppy * scale;
        game.ui_renderer.draw_bar(
            gl, pdx, pdy, 6.0, 6.0,
            1.0, [0.2, 0.9, 1.0, 1.0], [0.2, 0.9, 1.0, 1.0], &ui_proj,
        );

        // Enemy dots (red)
        for enemy in &game.enemies {
            if enemy.is_dead() { continue; }
            let (ex, ey) = enemy.position();
            let edx = map_left + ex * scale;
            let edy = map_top + ey * scale;
            game.ui_renderer.draw_bar(
                gl, edx, edy, 4.0, 4.0,
                1.0, [1.0, 0.2, 0.2, 1.0], [1.0, 0.2, 0.2, 1.0], &ui_proj,
            );
        }

        // Boss dot (purple)
        if let Some(ref boss) = game.boss {
            if !boss.is_dead() {
                let (bx, by) = boss.position();
                let bdx = map_left + bx * scale;
                let bdy = map_top + by * scale;
                game.ui_renderer.draw_bar(
                    gl, bdx, bdy, 6.0, 6.0,
                    1.0, [0.9, 0.1, 0.9, 1.0], [0.9, 0.1, 0.9, 1.0], &ui_proj,
                );
            }
        }

        // Bonfire dot (orange)
        let bfx = map_left + game.bonfire_x * scale;
        let bfy = map_top + game.bonfire_y * scale;
        game.ui_renderer.draw_bar(
            gl, bfx, bfy, 4.0, 4.0,
            1.0, [1.0, 0.7, 0.2, 1.0], [1.0, 0.7, 0.2, 1.0], &ui_proj,
        );
    }

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
            let t = game.death_anim_timer;
            // Fade to black over 1.5s
            let black_alpha = (t / 1.5).min(0.85);
            game.ui_renderer.draw_bar(
                gl, game.screen_w * 0.5, game.screen_h * 0.5,
                game.screen_w, game.screen_h,
                1.0,
                [0.0, 0.0, 0.0, black_alpha],
                [0.0, 0.0, 0.0, black_alpha],
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
        GameState::LevelUpMenu => {
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
        if matches!(game.state, GameState::TitleScreen | GameState::DeathScreen | GameState::BonfireMenu | GameState::LevelUpMenu) {
            let header = if game.state == GameState::LevelUpMenu {
                format!("<div class=\"menu-item\" style=\"color:#aaa;font-size:16px\">Level {} · Souls: {} · Cost: {}</div>", game.player.level, game.souls, game.player.level_up_cost())
            } else {
                String::new()
            };
            let html: String = game.menu.items.iter().enumerate().map(|(i, item)| {
                let extra = if game.state == GameState::LevelUpMenu && i < 3 {
                    match i {
                        0 => format!(" [{}]", game.player.vigor),
                        1 => format!(" [{}]", game.player.endurance),
                        2 => format!(" [{}]", game.player.strength),
                        _ => String::new(),
                    }
                } else { String::new() };
                if i == game.menu.selected_index {
                    format!("<div class=\"menu-item selected\">▸ {}{}</div>", item.label, extra)
                } else {
                    format!("<div class=\"menu-item\">{}{}</div>", item.label, extra)
                }
            }).collect::<Vec<_>>().join("");
            let _ = menu_el.set_attribute("style", "");
            menu_el.set_inner_html(&format!("{}{}", header, html));
        } else {
            let _ = menu_el.set_attribute("style", "display:none");
            menu_el.set_inner_html("");
        }
    }

    // Death title / Victory title
    if let Some(el) = document.get_element_by_id("death-title") {
        if game.state == GameState::DeathScreen {
            let t = game.death_anim_timer;
            // Text fades in after 0.5s, grows from small
            if t > 0.5 {
                let text_alpha = ((t - 0.5) / 1.0).min(1.0);
                let scale = 0.5 + text_alpha * 0.5;
                el.set_text_content(Some("YOU DIED"));
                let _ = el.set_attribute("style", &format!(
                    "opacity: {}; transform: translate(-50%, -50%) scale({:.2});",
                    text_alpha, scale
                ));
            } else {
                el.set_text_content(Some(""));
                let _ = el.set_attribute("style", "opacity: 0;");
            }
        } else if game.state == GameState::Victory {
            let mins = (game.play_time / 60.0) as u32;
            let secs = (game.play_time % 60.0) as u32;
            el.set_text_content(Some(&format!(
                "VICTORY\n\nTime: {}:{:02}\nEnemies Slain: {}\nDamage Dealt: {}\nDamage Taken: {}\nDeaths: {}\nLevel: {}\nSouls: {}\n\nPress Enter to return to title",
                mins, secs, game.enemies_killed, game.damage_dealt, game.damage_taken, game.death_count, game.player.level, game.souls
            )));
            let _ = el.set_attribute("style", "color: #e8c840; text-shadow: 0 0 20px rgba(232,200,64,0.6); white-space: pre-line;");
        } else {
            let _ = el.set_attribute("style", "display:none");
        }
    }

    // Level-up flash text
    if let Some(el) = document.get_element_by_id("level-up-text") {
        if game.level_up_flash > 0.0 {
            let alpha = (game.level_up_flash / 1.5).min(1.0);
            let _ = el.set_attribute("style", &format!("opacity: {}; color: #e8c840; font-size: 32px; text-shadow: 0 0 20px rgba(232,200,64,0.8); letter-spacing: 8px;", alpha));
            el.set_text_content(Some(&format!("LEVEL {}", game.player.level)));
        } else {
            let _ = el.set_attribute("style", "display:none");
            el.set_text_content(Some(""));
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
            "HP {}/{} | STA {}/{} | DMG {} | Lv{} | {} | {}",
            hp, max_hp, stamina, max_sta, game.player.damage(), game.player.level, state_name,
            game.player.weapon.name
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
            // Chest proximity hint
            for chest in &game.chests {
                if chest.opened { continue; }
                let cdx = px - chest.x;
                let cdy = py - chest.y;
                let cdist = (cdx * cdx + cdy * cdy).sqrt();
                if cdist < 30.0 {
                    text.push_str(" | [Enter] Open Chest");
                    break;
                }
            }
            // NPC proximity hint
            for npc in &game.npcs {
                let ndx = px - npc.x;
                let ndy = py - npc.y;
                let ndist = (ndx * ndx + ndy * ndy).sqrt();
                if ndist < 40.0 {
                    text.push_str(&format!(" | [Enter] Talk to {}", npc.name));
                    break;
                }
            }
        }
        el.set_text_content(Some(&text));
    }

    // Souls
    if let Some(el) = document.get_element_by_id("souls-text") {
        let mut text = format!("Souls: {} | Estus: {}/{}",
            game.souls, game.bonfire.estus_charges, game.bonfire.estus_max);
        if game.player.poison_timer > 0.0 {
            text.push_str(&format!(" | POISONED ({:.0}s)", game.player.poison_timer));
        }
        el.set_text_content(Some(&text));
        // Tint text when poisoned
        let _ = el.set_attribute("style", if game.player.poison_timer > 0.0 { "color: #6c6;" } else { "" });
    }

    // Boss name
    if let Some(el) = document.get_element_by_id("boss-name") {
        if let Some(ref boss) = game.boss {
            if !boss.is_dead() {
                if game.boss_intro_timer > 0.0 {
                    // Boss intro animation: big text fades in/out
                    let t = game.boss_intro_timer;
                    let alpha = if t > 2.0 {
                        (3.0 - t) / 1.0 // Fade in during first second
                    } else if t > 1.0 {
                        1.0 // Hold
                    } else {
                        t / 1.0 // Fade out
                    };
                    let _ = el.set_attribute("style", &format!(
                        "font-size: 42px; color: #e8c840; text-shadow: 0 0 30px rgba(232,200,64,0.8); opacity: {}; top: 25%; letter-spacing: 12px;",
                        alpha
                    ));
                    el.set_text_content(Some(&boss.name));
                } else {
                    let _ = el.set_attribute("style", "font-size: 14px; color: #c8c; top: 6px;");
                    el.set_text_content(Some(&format!("{} — HP: {}/{}", boss.name, boss.hp, boss.max_hp)));
                }
            } else {
                let _ = el.set_attribute("style", "display:none");
            }
        } else {
            let _ = el.set_attribute("style", "display:none");
        }
    }

    // NPC dialogue box — reuse boss-name element
    if let Some(el) = document.get_element_by_id("boss-name") {
        let talking_npc: Option<&Npc> = game.npcs.iter().find(|n| n.talking);
        if let Some(npc) = talking_npc {
            let line = npc.dialogue.get(npc.dialogue_index).map(|s| s.as_str()).unwrap_or("...");
            let text = format!("{}: {}", npc.name, line);
            let _ = el.set_attribute("style",
                "font-size: 16px; color: #eee; background: rgba(0,0,0,0.85); padding: 12px 24px; \
                 border: 1px solid #888; border-radius: 4px; top: 70%; left: 50%; \
                 transform: translateX(-50%); white-space: nowrap;");
            el.set_text_content(Some(&text));
        }
    }
}
