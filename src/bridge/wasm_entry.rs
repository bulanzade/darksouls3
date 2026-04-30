use crate::audio::audio_engine::AudioEngine;
use crate::core::camera::Camera2D;
use crate::core::input::InputState;
use crate::core::input::KeyCode;
use crate::core::time::{Time, FIXED_DT};
use crate::ai::state_machine::STAGGERED;
use crate::entity::boss::Boss;
use crate::entity::enemy::Enemy;
use crate::entity::entity_trait::{AttackTarget, DamageInfo, Entity, EntityId, EntityState};
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

#[derive(Clone, Copy, PartialEq, Debug, Eq, Hash)]
enum AreaId {
    CemeteryOfAsh,
    FirelinkShrine,
    LothricWall,
    UndeadSettlement,
    CathedralDeep,
    Irithyll,
}

fn area_name(area: AreaId) -> &'static str {
    match area {
        AreaId::CemeteryOfAsh => "灰烬墓地",
        AreaId::FirelinkShrine => "传火祭祀场",
        AreaId::LothricWall => "洛斯里克高墙",
        AreaId::UndeadSettlement => "不死聚落",
        AreaId::CathedralDeep => "幽邃教堂",
        AreaId::Irithyll => "冷冽谷的伊鲁席尔",
    }
}

fn area_boss(area: AreaId) -> Option<BossType> {
    match area {
        AreaId::CemeteryOfAsh => Some(BossType::IudexGundyr),
        AreaId::LothricWall => Some(BossType::Vordt),
        AreaId::UndeadSettlement => Some(BossType::DemonKnight),
        AreaId::CathedralDeep => Some(BossType::Dragonrider),
        AreaId::Irithyll => Some(BossType::RuinSentinel),
        _ => None,
    }
}

fn area_has_bonfire(area: AreaId) -> bool {
    area != AreaId::CemeteryOfAsh
}

use crate::entity::boss::BossType;

/// Stored area data — used to persist areas when switching between them
#[allow(dead_code)]
struct StoredArea {
    chunk: Chunk,
    collision: CollisionGrid,
    nav_grid: NavGrid,
    enemies: Vec<Enemy>,
    boss: Option<Boss>,
    items: Vec<WorldItem>,
    npcs: Vec<Npc>,
    chests: Vec<TreasureChest>,
    lights: Vec<Light>,
    fog_gates: Vec<FogGate>,
    bonfire_x: f32,
    bonfire_y: f32,
    boss_active: bool,
    boss_defeated: bool,
}

#[allow(dead_code)]
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
    // Secondary chunk for seamless neighbor rendering
    neighbor_chunk: Option<(AreaId, Chunk, CollisionGrid)>,
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
    lock_on_pos: Option<(f32, f32)>,
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
    pickup_notification: Option<(String, f32)>, // (text, timer)
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
    // Current area
    area: AreaId,
    // Fog gates (area transitions and boss doors)
    fog_gates: Vec<FogGate>,
    // Bosses defeated per area
    bosses_defeated: Vec<String>,
    // New Game+ cycle (0 = first playthrough, 1 = NG+, etc.)
    ng_plus: u32,
    // Inventory
    inventory: Vec<InventoryItem>,
    show_inventory: bool,
    // Stored areas (for seamless transitions — Cemetery ↔ Firelink)
    stored_areas: std::collections::HashMap<AreaId, StoredArea>,
    // Gundyr door state (opened after defeating boss)
    gundyr_door_open: bool,
    // Vordt defeated — demon transport pending
    vordt_transport_done: bool,
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
    ArmorDrop(ArmorSlot, String),  // (slot, armor name)
    RingDrop(String),               // ring name
}

#[derive(Clone, Copy, Debug, PartialEq)]
#[allow(dead_code)]
enum ArmorSlot {
    Head,
    Chest,
    Legs,
    Hands,
}

#[derive(Clone, Debug)]
struct InventoryItem {
    name: String,
    kind: InventoryItemKind,
}

#[derive(Clone, Debug)]
#[allow(dead_code)]
enum InventoryItemKind {
    Weapon(crate::combat::weapon::WeaponType),
    Armor(ArmorSlot, String),
    Ring(String),
    Consumable(String),
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
    is_mimic: bool,
    mimic_revealed: bool,
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
#[allow(dead_code)]
enum NpcKind {
    LevelUp,      // Emerald Herald — spend souls to level up
    Merchant,     // Buy items with souls
    Blacksmith,   // Upgrade weapons
    Dialogue,     // Story NPC — no shop
}

struct FogGate {
    x: f32,
    y: f32,
    w: f32,
    h: f32,
    destination: AreaId,
    dest_x: f32,
    dest_y: f32,
    active: bool, // deactivated after boss is dead
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
        area: AreaId::CemeteryOfAsh,
        fog_gates: vec![],
        bosses_defeated: vec![],
        ng_plus: 0,
        inventory: vec![],
        show_inventory: false,
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
        lock_on_pos: None,
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
            // Homeward Bone near bonfire
            WorldItem { x: 400.0, y: 600.0, kind: ItemKind::HomewardBone, collected: false },
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
        pickup_notification: None,
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
            TreasureChest { x: 480.0, y: 680.0, opened: false, loot: ItemKind::SoulOrb(500), is_mimic: false, mimic_revealed: false },
            TreasureChest { x: 560.0, y: 780.0, opened: false, loot: ItemKind::EstusShard, is_mimic: true, mimic_revealed: false },
            // Boss arena
            TreasureChest { x: 1780.0, y: 350.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::Uchigatana), is_mimic: false, mimic_revealed: false },
            // Corridor near poison
            TreasureChest { x: 1000.0, y: 900.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::GreatAxe), is_mimic: true, mimic_revealed: false },
        ],
        npcs: vec![
            // Emerald Herald at bonfire — level up NPC
            Npc {
                x: 240.0, y: 180.0,
                name: "绿衣使者".into(),
                color: [0.2, 0.9, 0.7, 1.0],
                dialogue: vec![
                    "欢迎来到传火祭祀场。".into(),
                    "你会一次又一次地失去灵魂。".into(),
                    "但不要害怕。寻找力量。其余的取决于你。".into(),
                    "[Enter] 升级".into(),
                ],
                dialogue_index: 0,
                talking: false,
                kind: NpcKind::LevelUp,
            },
            // Merchant in Room 3 — sells items
            Npc {
                x: 580.0, y: 720.0,
                name: "商人".into(),
                color: [0.8, 0.7, 0.3, 1.0],
                dialogue: vec![
                    "嘿嘿...看上什么了？".into(),
                    "我有原素碎片、紫苔藓...".into(),
                    "只需一点灵魂就好。".into(),
                    "[Enter] 购买原素碎片 (500灵魂)".into(),
                ],
                dialogue_index: 0,
                talking: false,
                kind: NpcKind::Merchant,
            },
        ],
        neighbor_chunk: None,
        stored_areas: std::collections::HashMap::new(),
        gundyr_door_open: false,
        vordt_transport_done: false,
    };

    unsafe {
        GAME = Some(game);
    }

    log::info!("DS3D initialized — WASD/arrows to move, Space to roll, E for estus");
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
        "q" | "Q" => 81,
        "Tab" => 9,
        "w" | "W" => 87,
        "1" => 49,
        "2" => 50,
        "mouse_left" => 128,
        "mouse_right" => 129,
        "wheel_up" => 130,
        "wheel_down" => 131,
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
        GameState::TravelMenu => update_travel_menu(game),
        GameState::Victory => update_victory(game),
        _ => {}
    }
}

fn update_title_screen(game: &mut Game) {
    if game.input.consume_pressed(KeyCode::Enter) {
        if let Some(action) = game.menu.current_action() {
            match action {
                MenuAction::NewGame => {
                    game.player = Player::new(1, 320.0, 320.0);
                    game.boss_defeated = false;
                    game.souls = 0;
                    game.bonfire = BonfireState::new();
                    game.enemies_killed = 0;
                    game.damage_dealt = 0;
                    game.damage_taken = 0;
                    game.death_count = 0;
                    game.play_time = 0.0;
                    game.bosses_defeated = vec![];
                    game.inventory = vec![];
                    game.has_bloodstain = false;
                    game.bloodstain_souls = 0;
                    load_area(game, AreaId::CemeteryOfAsh);
                }
                MenuAction::Continue => {
                    if let Some(save) = save_manager::load_from_localstorage() {
                        // Restore player stats first
                        game.player.level = save.player_level;
                        game.player.vigor = save.vigor;
                        game.player.endurance = save.endurance;
                        game.player.strength = save.strength;
                        game.player.apply_stats();
                        game.player.hp = save.player_hp;
                        // Restore weapon damage (upgrades)
                        game.player.weapon.base_damage = save.weapon_damage;
                        if let (Some(_), Some(dmg)) = (save.alt_weapon_name.as_ref(), save.alt_weapon_damage) {
                            if let Some(ref mut alt) = game.player.alt_weapon {
                                alt.base_damage = dmg;
                            }
                        }
                        game.souls = save.souls;
                        game.bonfire = save.bonfire.clone();
                        game.enemies_killed = save.enemies_killed;
                        game.play_time = save.play_time;
                        game.death_count = save.death_count;
                        game.damage_dealt = save.damage_dealt;
                        game.damage_taken = save.damage_taken;
                        game.bosses_defeated = save.bosses_defeated.clone();
                        // Determine saved area and load it
                        let saved_area = match save.current_room.as_str() {
                            "CemeteryOfAsh" => AreaId::CemeteryOfAsh,
                            "FirelinkShrine" | "Majula" => AreaId::FirelinkShrine,
                            "LothricWall" => AreaId::LothricWall,
                            "UndeadSettlement" | "ForestOfGiants" => AreaId::UndeadSettlement,
                            "CathedralDeep" => AreaId::CathedralDeep,
                            "Irithyll" | "LostBastille" => AreaId::Irithyll,
                            _ => AreaId::FirelinkShrine,
                        };
                        load_area(game, saved_area);
                        game.player.transform.x = save.player_x;
                        game.player.transform.y = save.player_y;
                        game.player.hp = save.player_hp;
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

fn rebuild_collision(game: &mut Game) {
    game.collision = CollisionGrid::from_chunk(&game.chunk, &game.tileset);
    game.nav_grid = NavGrid::from_collision_grid(&game.collision, CHUNK_SIZE, 2);
}

fn fill_tiles(chunk: &mut Chunk, tile: TileId, x1: usize, y1: usize, x2: usize, y2: usize) {
    debug_assert!(x1 <= x2 && y1 <= y2, "fill_tiles: inverted bounds ({x1},{y1})-({x2},{y2})");
    let max = CHUNK_SIZE - 1;
    for y in y1.min(max)..=y2.min(max) {
        for x in x1.min(max)..=x2.min(max) {
            chunk.tiles[y][x] = tile;
        }
    }
}

fn carve_ellipse(chunk: &mut Chunk, cx: i32, cy: i32, rx: i32, ry: i32) {
    let min_y = (cy - ry).max(0) as usize;
    let max_y = (cy + ry).min(CHUNK_SIZE as i32 - 1) as usize;
    let min_x = (cx - rx).max(0) as usize;
    let max_x = (cx + rx).min(CHUNK_SIZE as i32 - 1) as usize;
    for y in min_y..=max_y {
        for x in min_x..=max_x {
            let nx = (x as i32 - cx) as f32 / rx as f32;
            let ny = (y as i32 - cy) as f32 / ry as f32;
            if nx * nx + ny * ny <= 1.0 {
                chunk.tiles[y][x] = TileId::Ground;
            }
        }
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

    if game.area == AreaId::LothricWall && game.boss_defeated && !game.vordt_transport_done && game.slow_motion_timer <= 0.0 {
        game.vordt_transport_done = true;
        load_area(game, AreaId::UndeadSettlement);
        game.player.transform.x = 960.0;
        game.player.transform.y = 200.0;
        game.camera.x = 960.0;
        game.camera.y = 200.0;
        game.pickup_notification = Some(("恶魔将你运送至不死聚落...".into(), 3.0));
        return;
    }

    let mv = game.input.movement();
    let shift_held = game.input.held(KeyCode::Shift);
    let mouse_left = game.input.pressed(KeyCode::MouseLeft);
    let mouse_right = game.input.pressed(KeyCode::MouseRight);
    let attack = mouse_left && !shift_held;
    let heavy_attack = mouse_right && !shift_held;
    // Left hand: Shift+LMB = light attack (shield=block), Shift+RMB = heavy attack (shield=parry)
    let left_weapon = &game.player.equipment.left_hand.active();
    let has_shield = left_weapon.weapon_type == crate::combat::weapon::WeaponType::Shield;
    let left_light = mouse_left && shift_held; // Shield: block, Weapon: light attack
    let left_heavy = mouse_right && shift_held; // Shield: parry, Weapon: heavy attack
    let block_held = game.input.held(KeyCode::L) || (left_light && has_shield);
    let parry = left_heavy;
    let roll = game.input.pressed(KeyCode::Space);
    let estus = game.input.consume_pressed(KeyCode::E);
    let interact = game.input.consume_pressed(KeyCode::Enter);
    let lock_on_toggle = game.input.consume_pressed(KeyCode::Tab);
    let inventory_toggle = game.input.consume_pressed(KeyCode::I);
    let use_consumable = game.input.consume_pressed(KeyCode::Q);

    // Inventory toggle
    if inventory_toggle {
        game.show_inventory = !game.show_inventory;
    }
    // Skip game logic while inventory is open
    if game.show_inventory {
        return;
    }

    // Bonfire interaction (skip for first 0.5s after state change)
    if interact && game.state_timer > 0.5 && area_has_bonfire(game.area) {
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

    // Fog gate collision detection
    {
        let (px, py) = game.player.position();
        // Collect transitions first to avoid borrow issues
        let mut boss_spawn = None;
        let mut area_transition = None;
        for gate in &game.fog_gates {
            if !gate.active { continue; }
            let in_x = px > gate.x - gate.w * 0.5 && px < gate.x + gate.w * 0.5;
            let in_y = py > gate.y - gate.h * 0.5 && py < gate.y + gate.h * 0.5;
            if in_x && in_y {
                if gate.destination == game.area {
                    boss_spawn = Some((gate.dest_x, gate.dest_y));
                } else {
                    area_transition = Some((gate.destination, gate.dest_x, gate.dest_y));
                }
                break;
            }
        }
        if let Some((bx, by)) = boss_spawn {
            // Enter the boss room through the fog door, then activate the pre-spawned boss.
            game.player.transform.x = bx;
            game.player.transform.y = by;
            game.camera.x = bx;
            game.camera.y = by;
            if let Some(ref mut boss) = game.boss {
                if !boss.boss_activated && !boss.is_dead() {
                    boss.boss_activated = true;
                    game.boss_active = true;
                    game.boss_intro_timer = 3.0;
                    game.state_timer = 0.0;
                }
            }
        }
        if let Some((dest_area, dx, dy)) = area_transition {
            load_area(game, dest_area);
            game.player.transform.x = dx;
            game.player.transform.y = dy;
            game.camera.x = dx;
            game.camera.y = dy;
            return;
        }
    }

    // Cemetery and Firelink are connected by an unlocked doorway after Gundyr.

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
            // Spawn collection particles
            for i in 0..8 {
                let angle = i as f32 * std::f32::consts::TAU / 8.0;
                game.dust_particles.push(DustParticle {
                    x: item.x,
                    y: item.y,
                    vx: angle.cos() * 60.0,
                    vy: angle.sin() * 60.0,
                    timer: 0.4,
                });
            }
            match &item.kind {
                ItemKind::SoulOrb(n) => {
                    game.pickup_notification = Some((format!("获得 {} 灵魂", n), 2.0));
                    game.souls += *n;
                    game.audio.play_sfx("souls", 0.08, 0.0);
                }
                ItemKind::EstusShard => {
                    game.pickup_notification = Some(("获得 原素碎片".into(), 2.0));
                    game.bonfire.estus_max += 1;
                    game.bonfire.estus_charges = game.bonfire.estus_max;
                    game.audio.play_sfx("estus", 0.1, 0.0);
                }
                ItemKind::PurpleMoss => {
                    game.pickup_notification = Some(("获得 紫苔藓".into(), 2.0));
                    game.player.poison_timer = 0.0;
                    game.inventory.push(InventoryItem { name: "紫苔藓".into(), kind: InventoryItemKind::Consumable("PurpleMoss".into()) });
                    game.audio.play_sfx("estus", 0.08, 0.0);
                }
                ItemKind::HomewardBone => {
                    game.pickup_notification = Some(("获得 归还骨片".into(), 2.0));
                    game.inventory.push(InventoryItem { name: "归还骨片".into(), kind: InventoryItemKind::Consumable("HomewardBone".into()) });
                    game.audio.play_sfx("souls", 0.08, 0.0);
                }
                ItemKind::WeaponDrop(wt) => {
                    let wname = match wt {
                        crate::combat::weapon::WeaponType::GreatAxe => "大斧",
                        crate::combat::weapon::WeaponType::Dagger => "匕首",
                        crate::combat::weapon::WeaponType::Spear => "长枪",
                        crate::combat::weapon::WeaponType::Uchigatana => "打刀",
                        _ => "长剑",
                    };
                    game.pickup_notification = Some((format!("获得 {}", wname), 2.0));
                    game.inventory.push(InventoryItem { name: wname.into(), kind: InventoryItemKind::Weapon(*wt) });
                    // Also auto-equip to alt slot
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
                ItemKind::ArmorDrop(slot, name) => {
                    game.pickup_notification = Some((format!("获得 {}", name), 2.0));
                    game.inventory.push(InventoryItem { name: name.clone(), kind: InventoryItemKind::Armor(*slot, name.clone()) });
                    // Auto-equip
                    let armor = match name.as_str() {
                        "Hollow Soldier Helm" => crate::rpg::equipment::ArmorPiece::hollow_soldier_helm(),
                        "Hollow Soldier Armor" => crate::rpg::equipment::ArmorPiece::hollow_soldier_chest(),
                        "Knight Helm" => crate::rpg::equipment::ArmorPiece::knight_helm(),
                        "Knight Armor" => crate::rpg::equipment::ArmorPiece::knight_chest(),
                        _ => crate::rpg::equipment::ArmorPiece::none(),
                    };
                    match slot {
                        ArmorSlot::Head => game.player.equipment.head = armor,
                        ArmorSlot::Chest => game.player.equipment.chest = armor,
                        ArmorSlot::Legs => game.player.equipment.legs = armor,
                        ArmorSlot::Hands => game.player.equipment.hands = armor,
                    }
                    game.player.apply_stats();
                    game.audio.play_sfx("souls", 0.08, 0.0);
                }
                ItemKind::RingDrop(name) => {
                    game.pickup_notification = Some((format!("获得 {}", name), 2.0));
                    let ring = match name.as_str() {
                        "Life Ring" => crate::rpg::equipment::Ring::life_ring(),
                        "Chloranthy Ring" => crate::rpg::equipment::Ring::chloranthy(),
                        "Ring of the Lion" => crate::rpg::equipment::Ring::lion_ring(),
                        _ => return,
                    };
                    game.inventory.push(InventoryItem { name: name.clone(), kind: InventoryItemKind::Ring(name.clone()) });
                    if game.player.equipment.ring_1.is_none() {
                        game.player.equipment.ring_1 = Some(ring);
                    } else if game.player.equipment.ring_2.is_none() {
                        game.player.equipment.ring_2 = Some(ring);
                    }
                    game.player.apply_stats();
                    game.audio.play_sfx("souls", 0.08, 0.0);
                }
            }
        }
    }

    // Chest interaction
    if interact {
        for chest in &mut game.chests {
            if chest.opened || chest.mimic_revealed { continue; }
            let dx = px - chest.x;
            let dy = py - chest.y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < 30.0 {
                if chest.is_mimic {
                    chest.mimic_revealed = true;
                    game.camera.add_shake(6.0);
                    game.audio.play_sfx("boss_die", 0.2, 0.0);
                    game.pickup_notification = Some(("宝箱怪!".into(), 2.0));
                    // Spawn mimic enemy at chest position
                    let mimic_id = game.enemies.len() as u64 + 100;
                    game.enemies.push(crate::entity::enemy::Enemy::new_mimic(mimic_id, chest.x, chest.y));
                    // Force the mimic to activate immediately and aggro player
                    if let Some(mimic) = game.enemies.last_mut() {
                        mimic.mimic_activated = true;
                        mimic.aggro.check_detection(mimic.transform.x, mimic.transform.y, 1, px, py);
                    }
                    break;
                }
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
                    ItemKind::HomewardBone => {
                        game.inventory.push(InventoryItem { name: "Homeward Bone".into(), kind: InventoryItemKind::Consumable("HomewardBone".into()) });
                        game.audio.play_sfx("souls", 0.08, 0.0);
                    }
                    ItemKind::WeaponDrop(wt) => {
                        let wt_name = match wt {
                            crate::combat::weapon::WeaponType::Longsword => "直剑",
                            crate::combat::weapon::WeaponType::GreatAxe => "大斧",
                            crate::combat::weapon::WeaponType::Dagger => "匕首",
                            crate::combat::weapon::WeaponType::Spear => "长枪",
                            crate::combat::weapon::WeaponType::Uchigatana => "打刀",
                            crate::combat::weapon::WeaponType::Shield => "盾牌",
                        };
                        game.inventory.push(InventoryItem { name: wt_name.into(), kind: InventoryItemKind::Weapon(*wt) });
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
                    ItemKind::ArmorDrop(slot, name) => {
                        game.inventory.push(InventoryItem { name: name.clone(), kind: InventoryItemKind::Armor(*slot, name.clone()) });
                        let armor = match name.as_str() {
                            "Hollow Soldier Helm" => crate::rpg::equipment::ArmorPiece::hollow_soldier_helm(),
                            "Hollow Soldier Armor" => crate::rpg::equipment::ArmorPiece::hollow_soldier_chest(),
                            "Knight Helm" => crate::rpg::equipment::ArmorPiece::knight_helm(),
                            "Knight Armor" => crate::rpg::equipment::ArmorPiece::knight_chest(),
                            _ => crate::rpg::equipment::ArmorPiece::none(),
                        };
                        match slot {
                            ArmorSlot::Head => game.player.equipment.head = armor,
                            ArmorSlot::Chest => game.player.equipment.chest = armor,
                            ArmorSlot::Legs => game.player.equipment.legs = armor,
                            ArmorSlot::Hands => game.player.equipment.hands = armor,
                        }
                        game.player.apply_stats();
                        game.audio.play_sfx("souls", 0.08, 0.0);
                    }
                    ItemKind::RingDrop(name) => {
                        let ring = match name.as_str() {
                            "Life Ring" => crate::rpg::equipment::Ring::life_ring(),
                            "Chloranthy Ring" => crate::rpg::equipment::Ring::chloranthy(),
                            "Ring of the Lion" => crate::rpg::equipment::Ring::lion_ring(),
                            _ => return,
                        };
                        game.inventory.push(InventoryItem { name: name.clone(), kind: InventoryItemKind::Ring(name.clone()) });
                        if game.player.equipment.ring_1.is_none() {
                            game.player.equipment.ring_1 = Some(ring);
                        } else if game.player.equipment.ring_2.is_none() {
                            game.player.equipment.ring_2 = Some(ring);
                        }
                        game.player.apply_stats();
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
    if let Some((_, ref mut t)) = game.pickup_notification {
        *t -= dt;
        if *t <= 0.0 {
            game.pickup_notification = None;
        }
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
                            NpcKind::Blacksmith => {
                                if game.souls >= 1000 {
                                    game.souls -= 1000;
                                    game.player.weapon.base_damage += 15;
                                    if let Some(ref mut alt) = game.player.alt_weapon {
                                        alt.base_damage += 15;
                                    }
                                }
                            }
                            NpcKind::Dialogue => {}
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

    // Consumable items (Q key)
    if use_consumable {
        let moss_idx = game.inventory.iter().position(|i| matches!(&i.kind, InventoryItemKind::Consumable(n) if n == "PurpleMoss"));
        if let Some(idx) = moss_idx {
            game.player.poison_timer = 0.0;
            game.player.poison_tick = 0.0;
            game.inventory.remove(idx);
            game.audio.play_sfx("heal", 0.06, 0.0);
        } else {
            // Homeward Bone — teleport to last bonfire
            let bone_idx = game.inventory.iter().position(|i| matches!(&i.kind, InventoryItemKind::Consumable(n) if n == "HomewardBone"));
            if let Some(idx) = bone_idx {
                game.inventory.remove(idx);
                game.player.transform.x = game.bonfire_x;
                game.player.transform.y = game.bonfire_y;
                game.camera.x = game.bonfire_x;
                game.camera.y = game.bonfire_y;
                game.player.state = EntityState::Idle;
                game.audio.play_sfx("teleport", 0.08, 0.0);
            }
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
            if let Some(boss) = game.boss.as_ref() {
                if !boss.is_dead() && boss.boss_activated {
                    let (bx, by) = boss.position();
                    let d = ((px - bx) * (px - bx) + (py - by) * (py - by)).sqrt();
                    if best.map_or(true, |(_, bd)| d < bd) {
                        best = Some((boss.id(), d));
                    }
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
    game.lock_on_pos = if let Some(tid) = game.lock_on_target {
        game.enemies.iter().find(|e| e.id() == tid).map(|e| e.position())
            .or_else(|| game.boss.as_ref().and_then(|b| if b.id() == tid { Some(b.position()) } else { None }))
    } else {
        None
    };
    if let Some((tx, ty)) = game.lock_on_pos {
        let (px2, py2) = game.player.position();
        game.player.facing = (ty - py2).atan2(tx - px2);
    }

    // Weapon swap (1/2 keys)
    if game.input.consume_pressed(KeyCode::Num1) || game.input.consume_pressed(KeyCode::WheelUp) || game.input.consume_pressed(KeyCode::WheelDown) {
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
                        player.attack_timer = player.light_attack_duration();
                        player.is_heavy_attack = false;
                        player.attack_tracker.begin_attack();
                        game.input_buffer = BufferedAction::None;
                        game.input_buffer_timer = 0.0;
                    }
                }
                if do_heavy {
                    let cost = player.heavy_stamina_cost();
                    if player.stamina.consume(cost) {
                        player.state = EntityState::Attacking;
                        player.attack_timer = player.heavy_attack_duration();
                        player.is_heavy_attack = true;
                        player.attack_tracker.begin_attack();
                        game.input_buffer = BufferedAction::None;
                        game.input_buffer_timer = 0.0;
                    }
                }
                if block_held {
                    player.state = EntityState::Blocking;
                    player.parry_timer = player.parry_window;
                    player.block_timer = 0.0;
                }
                if parry {
                    player.state = EntityState::Blocking;
                    player.parry_timer = player.parry_window;
                    player.block_timer = 0.0;
                }
            }
            EntityState::Blocking => {
                if block_held {
                    player.block_timer = 0.0;
                } else if player.parry_timer > 0.0 {
                    // Stay in blocking during parry window even without block held
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
            let resist = game.player.equipment.poison_resist();
            if game.player.poison_timer <= 0.0 && resist < 1.0 {
                // Chance to resist based on equipment
                if (game.enemies_killed as f32 * 0.618).fract() >= resist {
                    game.player.poison_timer = 8.0 * (1.0 - resist); // Shorter with resist
                    game.player.poison_tick = 0.5;
                }
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

    // Boss AI update — during intro, boss stays in place
    if let Some(ref mut boss) = game.boss {
        if !boss.is_dead() {
            if game.boss_intro_timer > 0.0 {
                // Intro animation: boss stands still, only face the player
                let dx = px - boss.transform.x;
                let dy = py - boss.transform.y;
                boss.facing = dy.atan2(dx);
                boss.state = EntityState::Idle;
            } else {
                boss.update_ai(px, py, dt);
            }
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

    for enemy in &mut game.enemies {
        if enemy.is_dead() {
            continue;
        }
        let (ex, ey) = enemy.position();
        let dist = ((px - ex) * (px - ex) + (py - ey) * (py - ey)).sqrt();

        if player_attacking && dist < attack_range {
            let target = AttackTarget::Enemy(enemy.id());
            if !game.player.attack_tracker.has_hit(target) {
                game.player.attack_tracker.mark_hit(target);

                let blocked = enemy.try_block();
                let final_damage = if blocked { (attack_damage as f32 * 0.3) as i32 } else { attack_damage };
                let is_riposte = game.riposte_timer > 0.0 && game.riposte_target_id == enemy.id();
                let riposte_multiplier = if is_riposte { 3.0 } else { 1.0 };
                let actual_damage = (final_damage as f32 * riposte_multiplier) as i32;
                let dmg = DamageInfo {
                    damage: actual_damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: if is_heavy { 40.0 } else { 20.0 },
                    attacker_id: game.player.id(),
                    parryable: false,
                };
                let outcome = enemy.take_damage(&dmg);
                if !outcome.was_ignored {
                    game.camera.add_shake(if is_riposte { 10.0 } else if is_heavy { 6.0 } else { 3.0 });
                    game.hitstop_timer = if is_heavy { 0.05 } else { 0.02 };
                    game.audio.play_sfx("hit", if is_riposte { 0.2 } else { 0.12 }, 0.0);
                    game.damage_numbers.push(DamageNumber {
                        x: ex + ((game.damage_numbers.len() as f32 % 5.0) - 2.0) * 4.0,
                        y: ey - 24.0,
                        vy: -40.0,
                        value: outcome.actual_damage,
                        timer: 0.8,
                        is_player_damage: false,
                    });
                    game.damage_dealt += outcome.actual_damage as u32;
                    if blocked {
                        game.block_sparks.push(BlockSpark { x: ex, y: ey, timer: 0.3 });
                    } else {
                        game.stagger_bursts.push(BlockSpark { x: ex, y: ey, timer: 0.2 });
                    }
                }
                if is_riposte {
                    game.riposte_timer = 0.0;
                    game.riposte_target_id = 0;
                    game.screen_flash = Some(ScreenFlash { timer: 0.15, max_timer: 0.15, color: [1.0, 0.9, 0.3, 0.3] });
                }
                if outcome.killed {
                    game.enemies_killed += 1;
                    let soul_reward = match enemy.kind {
                        crate::entity::enemy::EnemyKind::HollowSoldier => 100,
                        crate::entity::enemy::EnemyKind::Archer => 150,
                        crate::entity::enemy::EnemyKind::Knight => 200,
                        crate::entity::enemy::EnemyKind::Assassin => 250,
                        crate::entity::enemy::EnemyKind::DarkMage => 300,
                        crate::entity::enemy::EnemyKind::Mimic => 500,
                        crate::entity::enemy::EnemyKind::CrystalLizard => 1200,
                    };
                    let soul_bonus = game.player.equipment.soul_bonus();
                    game.souls += (soul_reward as f32 * (1.0 + soul_bonus)) as u32;
                    game.camera.add_shake(6.0);
                    game.audio.play_sfx("enemy_die", 0.1, 0.0);
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
        }

        if *enemy.state() == EntityState::Attacking && enemy.windup_timer <= 0.0 && dist < enemy.attack_range && !enemy.has_hit_this_attack {
            if *game.player.state() != EntityState::Rolling {
                let dmg = DamageInfo {
                    damage: enemy.damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: 10.0,
                    attacker_id: enemy.id(),
                    parryable: enemy.current_attack_can_be_parried(),
                };
                let outcome = game.player.take_damage(&dmg);

                if outcome.was_parried {
                    enemy.fsm.current_state = STAGGERED;
                    enemy.fsm.state_timer = 0.0;
                    enemy.state = EntityState::Staggered;
                    enemy.parried_timer = 2.0;
                    enemy.has_hit_this_attack = true;
                    game.riposte_timer = 2.0;
                    game.riposte_target_id = enemy.id();
                    game.screen_flash = Some(ScreenFlash { timer: 0.12, max_timer: 0.12, color: [0.2, 1.0, 1.0, 0.4] });
                    game.stagger_bursts.push(BlockSpark { x: (px + ex) * 0.5, y: (py + ey) * 0.5, timer: 0.3 });
                    game.audio.play_sfx("hit", 0.15, 0.0);
                } else if outcome.was_blocked {
                    game.damage_taken += outcome.actual_damage as u32;
                    game.audio.play_sfx("hit", 0.08, 0.0);
                } else if outcome.actual_damage > 0 {
                    game.camera.add_shake(8.0);
                    game.audio.play_sfx("player_hit", 0.15, 0.0);
                    game.damage_taken += outcome.actual_damage as u32;
                    game.damage_numbers.push(DamageNumber {
                        x: px,
                        y: py - 24.0,
                        vy: -50.0,
                        value: outcome.actual_damage,
                        timer: 0.8,
                        is_player_damage: true,
                    });
                }
                enemy.has_hit_this_attack = true;
            }
        }
    }

    // --- Combat: player vs boss ---
    let mut gundyr_door = false;
    if let Some(ref mut boss) = game.boss {
        let (bx, by) = boss.position();
        let dist = ((px - bx) * (px - bx) + (py - by) * (py - by)).sqrt();

        if player_attacking && dist < attack_range + 16.0 && game.boss_intro_timer <= 0.0 {
            let target = AttackTarget::Boss(boss.id());
            if !game.player.attack_tracker.has_hit(target) {
                game.player.attack_tracker.mark_hit(target);
                let dmg = DamageInfo {
                    damage: attack_damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: if is_heavy { 40.0 } else { 20.0 },
                    attacker_id: game.player.id(),
                    parryable: false,
                };
                let outcome = boss.take_damage(&dmg);
                if !outcome.was_ignored {
                    game.damage_dealt += outcome.actual_damage as u32;
                    game.damage_numbers.push(DamageNumber {
                        x: bx,
                        y: by - 36.0,
                        vy: -42.0,
                        value: outcome.actual_damage,
                        timer: 0.8,
                        is_player_damage: false,
                    });
                    game.camera.add_shake(if is_heavy { 8.0 } else { 4.0 });
                    game.audio.play_sfx("hit", 0.12, 0.0);
                }
                if outcome.killed && !game.boss_defeated {
                    game.boss_defeated = true;
                    let boss_name = match boss.boss_type {
                        BossType::IudexGundyr => "IudexGundyr",
                        BossType::Vordt => "Vordt",
                        BossType::DemonKnight => "CurseRottedGreatwood",
                        BossType::Dragonrider => "DeaconsOfTheDeep",
                        BossType::RuinSentinel => "PontiffSulyvahn",
                    };
                    if !game.bosses_defeated.iter().any(|b| b == boss_name) {
                        game.bosses_defeated.push(boss_name.into());
                    }
                    gundyr_door = boss.boss_type == BossType::IudexGundyr && !game.gundyr_door_open;
                    for gate in &mut game.fog_gates {
                        if gate.destination == game.area {
                            gate.active = false;
                        }
                    }
                    if game.bosses_defeated.len() >= 5 {
                        game.state = GameState::Victory;
                    }
                    game.souls += 5000;
                    game.camera.add_shake(15.0);
                    game.slow_motion_timer = 1.5;
                    game.audio.play_sfx("boss_die", 0.2, 0.0);
                }
            }
        }

        if boss.current_attack_can_hit(px, py) && game.boss_intro_timer <= 0.0 {
            if *game.player.state() != EntityState::Rolling {
                let dmg = DamageInfo {
                    damage: boss.damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: 15.0,
                    attacker_id: boss.id(),
                    parryable: boss.current_attack_can_be_parried(),
                };
                let outcome = game.player.take_damage(&dmg);

                if outcome.was_parried && boss.current_attack_can_be_parried() {
                    boss.state = EntityState::Staggered;
                    boss.stagger_timer = 2.0;
                    game.riposte_timer = 2.0;
                    game.riposte_target_id = boss.id();
                    game.screen_flash = Some(ScreenFlash { timer: 0.12, max_timer: 0.12, color: [0.2, 1.0, 1.0, 0.4] });
                    game.stagger_bursts.push(BlockSpark { x: (px + bx) * 0.5, y: (py + by) * 0.5, timer: 0.3 });
                    game.audio.play_sfx("hit", 0.18, 0.0);
                } else if outcome.was_blocked {
                    game.damage_taken += outcome.actual_damage as u32;
                    game.audio.play_sfx("hit", 0.1, 0.0);
                } else if outcome.actual_damage > 0 {
                    game.camera.add_shake(12.0);
                    game.audio.play_sfx("player_hit", 0.18, 0.0);
                    game.damage_taken += outcome.actual_damage as u32;
                    game.damage_numbers.push(DamageNumber {
                        x: px,
                        y: py - 24.0,
                        vy: -50.0,
                        value: outcome.actual_damage,
                        timer: 0.8,
                        is_player_damage: true,
                    });
                }
                boss.mark_current_hit_window();
            }
        }
    }

    // Open Gundyr's door after defeat
    if gundyr_door {
        game.gundyr_door_open = true;
        fill_tiles(&mut game.chunk, TileId::Ground, 16, 8, 40, 18);
        for gate in &mut game.fog_gates {
            if gate.destination == AreaId::FirelinkShrine {
                gate.active = true;
            }
        }
        rebuild_collision(game);
    }

    // --- Spawn boss when mini-boss (last enemy) is killed ---
    // Only auto-spawn in areas without a dedicated fog gate boss
    let has_area_boss = area_boss(game.area).is_some();
    if !has_area_boss && !game.boss_active && !game.boss_defeated && game.enemies.last().map_or(false, |e| e.is_dead()) {
        let boss_type = (game.enemies_killed * 1103515245 + 12345) as usize % 3;
        let (px, py) = game.player.position();
        let spawn_x = px + 200.0;
        let spawn_y = py;
        game.boss = Some(match boss_type {
            0 => Boss::new_test_boss(10, spawn_x, spawn_y),
            1 => Boss::new_dragonrider(10, spawn_x, spawn_y),
            _ => Boss::new_ruin_sentinel(10, spawn_x, spawn_y),
        });
        game.boss_active = true;
        game.boss_intro_timer = 3.0;
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
                    parryable: false,
                };
                let outcome = game.player.take_damage(&dmg);
                if outcome.was_blocked || outcome.was_parried {
                    game.audio.play_sfx("hit", 0.08, 0.0);
                } else if outcome.actual_damage > 0 {
                    game.damage_taken += outcome.actual_damage as u32;
                    game.camera.add_shake(4.0);
                    game.audio.play_sfx("player_hit", 0.1, 0.0);
                    game.damage_numbers.push(DamageNumber {
                        x: px,
                        y: py - 24.0,
                        vy: -50.0,
                        value: outcome.actual_damage,
                        timer: 0.8,
                        is_player_damage: true,
                    });
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
    if let Some((tx, ty)) = game.lock_on_pos {
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

    // Check victory — only if all five area bosses are defeated
    if game.boss_defeated && game.bosses_defeated.len() >= 5 && game.slow_motion_timer <= 0.0 {
        game.state = GameState::Victory;
        game.audio.play_sfx("victory", 0.12, 0.0);
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
                    // Respawn at bonfire — reload current area
                    game.souls = 0;
                    game.bonfire.rest();
                    game.bonfire.estus_charges = game.bonfire.estus_max;
                    let current_area = game.area;
                    load_area(game, current_area);
                    game.player.hp = game.player.max_hp;
                    game.player.state = EntityState::Idle;
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
                    game.player.poison_timer = 0.0;
                    // Reload current area to respawn enemies
                    let current_area = game.area;
                    load_area(game, current_area);
                    game.player.hp = game.player.max_hp;
                    // Auto-save at bonfire
                    let (px, py) = game.player.position();
                    let save = SaveData {
                        player_level: game.player.level,
                        vigor: game.player.vigor,
                        endurance: game.player.endurance,
                        strength: game.player.strength,
                        souls: game.souls,
                        bonfire: game.bonfire.clone(),
                        current_room: format!("{:?}", game.area),
                        player_hp: game.player.hp,
                        player_x: px,
                        player_y: py,
                        weapon_name: game.player.weapon.name.clone(),
                        weapon_damage: game.player.weapon.base_damage,
                        alt_weapon_name: game.player.alt_weapon.as_ref().map(|w| w.name.clone()),
                        alt_weapon_damage: game.player.alt_weapon.as_ref().map(|w| w.base_damage),
                        bosses_defeated: game.bosses_defeated.clone(),
                        enemies_killed: game.enemies_killed,
                        items_collected: game.items.iter().filter(|i| i.collected).map(|_| "item".into()).collect(),
                        chests_opened: game.chests.iter().filter(|c| c.opened || c.mimic_revealed).map(|_| "chest".into()).collect(),
                        play_time: game.play_time,
                        death_count: game.death_count,
                        damage_dealt: game.damage_dealt,
                        damage_taken: game.damage_taken,
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
                MenuAction::Travel => {
                    game.state = GameState::TravelMenu;
                    game.menu = MenuState::travel_menu();
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

fn load_area(game: &mut Game, area: AreaId) {
    let player_hp_ratio = game.player.hp as f32 / game.player.max_hp as f32;
    game.area = area;
    game.state = GameState::Playing;
    game.time.accumulator = 0.0;
    game.state_timer = 0.0;
    game.lock_on_target = None;

    // Clear transient state
    game.projectiles.clear();
    game.soul_orbs.clear();
    game.death_particles.clear();
    game.damage_numbers.clear();
    game.boss = None;
    game.boss_active = false;
    game.boss_defeated = false;
    game.dust_particles.clear();
    game.block_sparks.clear();
    game.stagger_bursts.clear();
    game.screen_flash = None;
    game.input_buffer = BufferedAction::None;
    game.input_buffer_timer = 0.0;

    match area {
        AreaId::CemeteryOfAsh => {
            let mut chunk = Chunk::new((0, 0));
            for y in 0..CHUNK_SIZE { for x in 0..CHUNK_SIZE { chunk.tiles[y][x] = TileId::Wall; } }

            // Player wakes in the lower-left grave pocket.
            carve_ellipse(&mut chunk, 12, 103, 8, 6);
            fill_tiles(&mut chunk, TileId::Ground, 12, 96, 23, 108);
            carve_ellipse(&mut chunk, 28, 91, 12, 8);
            fill_tiles(&mut chunk, TileId::Ground, 22, 86, 39, 98);

            // Main cemetery route bends upward and right toward Gundyr.
            fill_tiles(&mut chunk, TileId::Ground, 34, 76, 47, 91);
            carve_ellipse(&mut chunk, 48, 70, 15, 10);
            fill_tiles(&mut chunk, TileId::Ground, 45, 62, 64, 76);
            carve_ellipse(&mut chunk, 65, 56, 17, 10);
            fill_tiles(&mut chunk, TileId::Ground, 61, 48, 77, 64);
            carve_ellipse(&mut chunk, 79, 41, 13, 9);

            // Right-lower optional branch: crystal lizard mini-boss dead end.
            fill_tiles(&mut chunk, TileId::Ground, 38, 84, 58, 94);
            fill_tiles(&mut chunk, TileId::Ground, 56, 90, 78, 102);
            carve_ellipse(&mut chunk, 91, 104, 19, 12);
            fill_tiles(&mut chunk, TileId::Poison, 86, 99, 97, 109);
            fill_tiles(&mut chunk, TileId::Ground, 88, 101, 94, 106);

            // Gundyr arena in the upper-right, entered through a wall-mounted fog door.
            fill_tiles(&mut chunk, TileId::Ground, 76, 33, 88, 42);
            carve_ellipse(&mut chunk, 96, 30, 22, 18);
            carve_ellipse(&mut chunk, 96, 30, 16, 12);
            for x in 70..CHUNK_SIZE { chunk.tiles[43][x] = TileId::Wall; }
            fill_tiles(&mut chunk, TileId::Ground, 78, 41, 90, 45);
            for x in 72..CHUNK_SIZE { chunk.tiles[10][x] = TileId::Wall; }
            for y in 10..51 { chunk.tiles[y][71] = TileId::Wall; chunk.tiles[y][CHUNK_SIZE - 1] = TileId::Wall; }
            for y in 43..51 { chunk.tiles[y][118] = TileId::Wall; }

            // Post-Gundyr route turns west/up to the locked Firelink door.
            fill_tiles(&mut chunk, TileId::Ground, 84, 28, 96, 44);
            fill_tiles(&mut chunk, TileId::Ground, 62, 18, 88, 34);
            fill_tiles(&mut chunk, TileId::Ground, 36, 10, 66, 24);
            fill_tiles(&mut chunk, TileId::Ground, 16, 8, 40, 18);
            for y in 6..21 { chunk.tiles[y][15] = TileId::Wall; }
            for x in 16..41 { chunk.tiles[7][x] = TileId::Wall; }

            // Gravestones and coffins define cover without blocking the main routes.
            fill_tiles(&mut chunk, TileId::Wall, 42, 84, 45, 87);
            fill_tiles(&mut chunk, TileId::Wall, 30, 88, 33, 91);
            fill_tiles(&mut chunk, TileId::Wall, 58, 64, 61, 67);
            fill_tiles(&mut chunk, TileId::Wall, 88, 20, 91, 23);
            fill_tiles(&mut chunk, TileId::Wall, 106, 35, 109, 38);

            game.chunk = chunk;
            game.collision = CollisionGrid::from_chunk(&game.chunk, &game.tileset);
            game.nav_grid = NavGrid::from_collision_grid(&game.collision, CHUNK_SIZE, 2);
            game.player.transform.x = 200.0;
            game.player.transform.y = 1660.0;
            game.player.hp = game.player.max_hp;
            game.enemies = vec![
                Enemy::new_hollow_soldier(2, 470.0, 1450.0),
                Enemy::new_hollow_soldier(3, 760.0, 1120.0),
                Enemy::new_archer(4, 1120.0, 880.0),
                Enemy::new_knight(5, 1180.0, 730.0),
                Enemy::new_hollow_soldier(6, 1040.0, 850.0),
                Enemy::new_crystal_lizard(7, 1450.0, 1660.0),
            ];
            game.items = vec![
                WorldItem { x: 210.0, y: 1620.0, kind: ItemKind::SoulOrb(100), collected: false },
                WorldItem { x: 760.0, y: 1140.0, kind: ItemKind::SoulOrb(150), collected: false },
                WorldItem { x: 1360.0, y: 650.0, kind: ItemKind::HomewardBone, collected: false },
                WorldItem { x: 1500.0, y: 1700.0, kind: ItemKind::EstusShard, collected: false },
                WorldItem { x: 1800.0, y: 640.0, kind: ItemKind::SoulOrb(300), collected: false },
            ];
            game.chests = vec![
                TreasureChest { x: 1570.0, y: 1710.0, opened: false, loot: ItemKind::SoulOrb(500), is_mimic: false, mimic_revealed: false },
            ];
            game.npcs = vec![];
            game.lights = vec![
                Light { x: 200.0, y: 1660.0, radius: 190.0, color: [0.82, 0.78, 0.62], intensity: 0.22 },
                Light { x: 760.0, y: 1120.0, radius: 170.0, color: [0.78, 0.58, 0.34], intensity: 0.14 },
                Light { x: 1450.0, y: 1660.0, radius: 210.0, color: [0.55, 0.75, 0.9], intensity: 0.18 },
                Light { x: 1460.0, y: 620.0, radius: 360.0, color: [0.55, 0.52, 0.62], intensity: 0.22 },
                Light { x: 1800.0, y: 720.0, radius: 220.0, color: [0.72, 0.62, 0.48], intensity: 0.18 },
            ];
            game.bonfire_x = -10000.0;
            game.bonfire_y = -10000.0;
            // Gundyr fog activates the boss; the upper-left Firelink door opens after he dies.
            let gundyr_defeated = game.bosses_defeated.iter().any(|b| b == "IudexGundyr");
            game.fog_gates = vec![
                FogGate { x: 1312.0, y: 688.0, w: 192.0, h: 28.0, destination: AreaId::CemeteryOfAsh, dest_x: 1470.0, dest_y: 520.0, active: !gundyr_defeated },
                FogGate { x: 360.0, y: 160.0, w: 120.0, h: 32.0, destination: AreaId::FirelinkShrine, dest_x: 960.0, dest_y: 160.0, active: gundyr_defeated },
            ];
            // If Gundyr door was previously opened, keep it open
            if game.gundyr_door_open {
                fill_tiles(&mut game.chunk, TileId::Ground, 16, 8, 40, 18);
                rebuild_collision(game);
            }
        }
        AreaId::FirelinkShrine => {
            // Firelink Shrine: hub with bonfire, NPCs, paths to other areas
            // Layout: central plaza with bonfire, buildings to west, cliff path east, sunken path south
            let mut chunk = Chunk::new((0, 0));
            for y in 0..CHUNK_SIZE { for x in 0..CHUNK_SIZE { chunk.tiles[y][x] = TileId::Wall; } }
            // Central plaza (wide open area around bonfire)
            for y in 8..40 { for x in 10..50 { chunk.tiles[y][x] = TileId::Ground; } }
            // Western building interior (Blacksmith's shop)
            for y in 15..25 { for x in 2..12 { chunk.tiles[y][x] = TileId::Ground; } }
            // Eastern cliff path (winding toward Undead Settlement)
            for y in 20..35 { for x in 50..65 { chunk.tiles[y][x] = TileId::Ground; } }
            // Elevated platform (monument area)
            for y in 5..15 { for x in 20..35 { chunk.tiles[y][x] = TileId::Ground; } }
            // Northern entrance from Cemetery of Ash, reached after Gundyr.
            for y in 0..10 { for x in 50..70 { chunk.tiles[y][x] = TileId::Ground; } }
            // Connect north entrance to central plaza.
            for y in 8..15 { for x in 28..70 { chunk.tiles[y][x] = TileId::Ground; } }
            // Southern sunken path (toward Cathedral)
            for y in 38..55 { for x in 20..35 { chunk.tiles[y][x] = TileId::Ground; } }
            // Southeast path (toward Cathedral of the Deep)
            for y in 35..50 { for x in 40..55 { chunk.tiles[y][x] = TileId::Ground; } }
            // Water/shore (coastal edge)
            for y in 30..40 { for x in 42..50 { chunk.tiles[y][x] = TileId::Poison; } }

            game.chunk = chunk;
            game.collision = CollisionGrid::from_chunk(&game.chunk, &game.tileset);
            game.nav_grid = NavGrid::from_collision_grid(&game.collision, CHUNK_SIZE, 2);
            game.player.transform.x = 320.0;
            game.player.transform.y = 320.0;
            game.player.hp = game.player.max_hp;
            game.enemies = vec![];
            game.items = vec![
                WorldItem { x: 450.0, y: 200.0, kind: ItemKind::SoulOrb(100), collected: false },
            ];
            game.chests = vec![];
            game.npcs = vec![
                Npc { x: 360.0, y: 300.0, name: "防火女".into(), color: [0.2, 0.9, 0.7, 1.0],
                    dialogue: vec!["欢迎来到传火祭祀场，无火的余灰。".into(), "薪王们已离开了他们的王座。".into(),
                        "请将他们带回原本的位置。".into(), "[Enter] 升级".into()],
                    dialogue_index: 0, talking: false, kind: NpcKind::LevelUp },
                Npc { x: 300.0, y: 380.0, name: "安德烈".into(), color: [0.7, 0.5, 0.2, 1.0],
                    dialogue: vec!["我是安德烈，祭祀场的铁匠。".into(), "交给我吧，你的武器会焕然一新。".into(),
                        "[Enter] 强化武器 (1000灵魂)".into()],
                    dialogue_index: 0, talking: false, kind: NpcKind::Blacksmith },
                Npc { x: 380.0, y: 400.0, name: "侍女".into(), color: [0.8, 0.7, 0.3, 1.0],
                    dialogue: vec!["你好啊，无火的余灰。".into(), "我这里有各种各样好东西。".into(),
                        "[Enter] 购买原素碎片 (500灵魂)".into()],
                    dialogue_index: 0, talking: false, kind: NpcKind::Merchant },
            ];
            game.lights = vec![
                Light { x: 320.0, y: 320.0, radius: 300.0, color: [0.95, 0.9, 0.7], intensity: 0.5 },
                Light { x: 300.0, y: 380.0, radius: 150.0, color: [0.9, 0.6, 0.3], intensity: 0.2 },
                Light { x: 380.0, y: 400.0, radius: 150.0, color: [0.9, 0.6, 0.3], intensity: 0.2 },
            ];
            game.bonfire_x = 320.0;
            game.bonfire_y = 320.0;
            game.fog_gates = vec![
                FogGate { x: 855.0, y: 380.0, w: 64.0, h: 120.0, destination: AreaId::UndeadSettlement, dest_x: 200.0, dest_y: 200.0, active: true },
                FogGate { x: 380.0, y: 700.0, w: 80.0, h: 32.0, destination: AreaId::CathedralDeep, dest_x: 200.0, dest_y: 200.0, active: true },
                FogGate { x: 960.0, y: 64.0, w: 120.0, h: 32.0, destination: AreaId::CemeteryOfAsh, dest_x: 360.0, dest_y: 220.0, active: true },
            ];
        }
        AreaId::LothricWall => {
            // Lothric Wall: high stone walls, dragon courtyard, Vordt boss
            // Layout: entry ramparts → dragon courtyard → lower streets → boss arena
            let mut chunk = Chunk::new((0, 0));
            for y in 0..CHUNK_SIZE { for x in 0..CHUNK_SIZE { chunk.tiles[y][x] = TileId::Wall; } }
            // Entry ramparts (upper walls, narrow path)
            for y in 5..25 { for x in 5..35 { chunk.tiles[y][x] = TileId::Ground; } }
            // Dragon courtyard (wide open area with dragon perch)
            for y in 10..40 { for x in 30..70 { chunk.tiles[y][x] = TileId::Ground; } }
            // Dragon perch (elevated platform — wall-topped)
            for y in 15..20 { for x in 55..65 { chunk.tiles[y][x] = TileId::Wall; } }
            // Lower streets (winding path through ruins)
            for y in 35..55 { for x in 20..55 { chunk.tiles[y][x] = TileId::Ground; } }
            // Side alleys
            for y in 20..35 { for x in 65..90 { chunk.tiles[y][x] = TileId::Ground; } }
            // Market square
            for y in 45..70 { for x in 40..80 { chunk.tiles[y][x] = TileId::Ground; } }
            // Underground passage
            for y in 65..80 { for x in 50..65 { chunk.tiles[y][x] = TileId::Ground; } }
            // Boss arena (enclosed — Vordt)
            for y in 80..105 { for x in 35..65 { chunk.tiles[y][x] = TileId::Ground; } }
            // Arena walls with north door (x:45..55)
            for x in 35..45 { chunk.tiles[79][x] = TileId::Wall; }
            for x in 55..65 { chunk.tiles[79][x] = TileId::Wall; }
            for x in 35..65 { chunk.tiles[105][x] = TileId::Wall; }
            for y in 79..106 { chunk.tiles[y][34] = TileId::Wall; }
            for y in 79..106 { chunk.tiles[y][65] = TileId::Wall; }
            // Debris in streets
            for x in 25..30 { for y in 40..45 { chunk.tiles[y][x] = TileId::Wall; } }
            for x in 70..75 { for y in 55..60 { chunk.tiles[y][x] = TileId::Wall; } }
            // Bonfire near entry
            game.bonfire_x = 200.0;
            game.bonfire_y = 200.0;

            game.chunk = chunk;
            game.collision = CollisionGrid::from_chunk(&game.chunk, &game.tileset);
            game.nav_grid = NavGrid::from_collision_grid(&game.collision, CHUNK_SIZE, 2);
            game.player.transform.x = 200.0;
            game.player.transform.y = 200.0;
            game.player.hp = (game.player.max_hp as f32 * player_hp_ratio) as i32;
            game.enemies = vec![
                // Entry ramparts
                Enemy::new_hollow_soldier(2, 300.0, 150.0),
                Enemy::new_archer(3, 400.0, 250.0),
                // Dragon courtyard
                Enemy::new_knight(4, 600.0, 300.0),
                Enemy::new_hollow_soldier(5, 700.0, 400.0),
                Enemy::new_archer(6, 800.0, 350.0),
                // Side alleys
                Enemy::new_assassin(7, 1200.0, 400.0),
                Enemy::new_hollow_soldier(8, 1100.0, 500.0),
                // Lower streets
                Enemy::new_knight(9, 500.0, 650.0),
                Enemy::new_dark_mage(10, 600.0, 750.0),
                // Market square
                Enemy::new_hollow_soldier(11, 700.0, 950.0),
                Enemy::new_knight(12, 900.0, 1000.0),
                Enemy::new_archer(13, 1000.0, 1100.0),
                Enemy::new_dark_mage(14, 800.0, 1150.0),
                // Near boss
                Enemy::new_knight(15, 750.0, 1300.0),
                Enemy::new_mini_boss(16, 800.0, 1400.0),
            ];
            game.items = vec![
                WorldItem { x: 250.0, y: 200.0, kind: ItemKind::SoulOrb(200), collected: false },
                WorldItem { x: 700.0, y: 350.0, kind: ItemKind::SoulOrb(300), collected: false },
                WorldItem { x: 1200.0, y: 450.0, kind: ItemKind::EstusShard, collected: false },
                WorldItem { x: 500.0, y: 700.0, kind: ItemKind::SoulOrb(200), collected: false },
                WorldItem { x: 800.0, y: 1000.0, kind: ItemKind::PurpleMoss, collected: false },
                WorldItem { x: 950.0, y: 1100.0, kind: ItemKind::SoulOrb(500), collected: false },
                WorldItem { x: 700.0, y: 1350.0, kind: ItemKind::SoulOrb(1000), collected: false },
                WorldItem { x: 600.0, y: 1500.0, kind: ItemKind::EstusShard, collected: false },
            ];
            game.chests = vec![
                TreasureChest { x: 350.0, y: 300.0, opened: false, loot: ItemKind::SoulOrb(300), is_mimic: false, mimic_revealed: false },
                TreasureChest { x: 1100.0, y: 500.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::Spear), is_mimic: false, mimic_revealed: false },
                TreasureChest { x: 900.0, y: 1050.0, opened: false, loot: ItemKind::ArmorDrop(ArmorSlot::Chest, "Knight Armor".into()), is_mimic: true, mimic_revealed: false },
                TreasureChest { x: 650.0, y: 1450.0, opened: false, loot: ItemKind::RingDrop("Steel Protection".into()), is_mimic: false, mimic_revealed: false },
            ];
            game.npcs = vec![];
            game.lights = vec![
                Light { x: 200.0, y: 200.0, radius: 250.0, color: [0.9, 0.8, 0.6], intensity: 0.4 },
                Light { x: 700.0, y: 350.0, radius: 200.0, color: [0.5, 0.5, 0.7], intensity: 0.2 },
                Light { x: 1000.0, y: 500.0, radius: 180.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
                Light { x: 600.0, y: 700.0, radius: 200.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
                Light { x: 800.0, y: 1050.0, radius: 200.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
                Light { x: 900.0, y: 1400.0, radius: 220.0, color: [0.4, 0.5, 0.8], intensity: 0.25 },
            ];
            let vordt_defeated = game.bosses_defeated.iter().any(|b| b == "Vordt");
            game.fog_gates = vec![
                // Boss fog gate at arena north entrance
                FogGate { x: 800.0, y: 1264.0, w: 128.0, h: 32.0, destination: AreaId::LothricWall, dest_x: 960.0, dest_y: 1500.0, active: !vordt_defeated },
            ];
        }
        AreaId::UndeadSettlement => {
            // Undead Settlement: dense forest with ruins, hollow camps, river
            // Layout: entrance clearing → hollow camp → stone ruins → underground river → boss arena
            let mut chunk = Chunk::new((0, 0));
            for y in 0..CHUNK_SIZE { for x in 0..CHUNK_SIZE { chunk.tiles[y][x] = TileId::Wall; } }
            // Entrance clearing (near bonfire)
            for y in 5..25 { for x in 5..30 { chunk.tiles[y][x] = TileId::Ground; } }
            // Hollow camp (open area with scattered enemies)
            for y in 15..40 { for x in 20..55 { chunk.tiles[y][x] = TileId::Ground; } }
            // Stone ruins (crumbled walls forming corridors)
            for y in 35..55 { for x in 15..40 { chunk.tiles[y][x] = TileId::Ground; } }
            // River crossing (narrow bridge area)
            for y in 40..50 { for x in 40..65 { chunk.tiles[y][x] = TileId::Ground; } }
            // Far forest (dense trees opening to wider area)
            for y in 50..80 { for x in 30..75 { chunk.tiles[y][x] = TileId::Ground; } }
            // Underground passage (narrow tunnel)
            for y in 75..90 { for x in 40..55 { chunk.tiles[y][x] = TileId::Ground; } }
            // Boss arena (enclosed room — walls on all sides, door on north side)
            // Room interior: y:90..110, x:35..65
            for y in 90..110 { for x in 35..65 { chunk.tiles[y][x] = TileId::Ground; } }
            // North wall with door gap (x:45..55 = opening)
            for x in 35..45 { chunk.tiles[89][x] = TileId::Wall; }
            for x in 55..65 { chunk.tiles[89][x] = TileId::Wall; }
            // South wall (solid)
            for x in 35..65 { chunk.tiles[110][x] = TileId::Wall; }
            // West wall (solid)
            for y in 89..111 { chunk.tiles[y][34] = TileId::Wall; }
            // East wall (solid)
            for y in 89..111 { chunk.tiles[y][65] = TileId::Wall; }
            // Side paths (hidden areas with items)
            for y in 8..20 { for x in 50..75 { chunk.tiles[y][x] = TileId::Ground; } }
            // Poison swamp (south of ruins)
            for y in 42..52 { for x in 55..70 { chunk.tiles[y][x] = TileId::Poison; } }

            game.chunk = chunk;
            game.collision = CollisionGrid::from_chunk(&game.chunk, &game.tileset);
            game.nav_grid = NavGrid::from_collision_grid(&game.collision, CHUNK_SIZE, 2);
            game.player.transform.x = 200.0;
            game.player.transform.y = 200.0;
            game.player.hp = (game.player.max_hp as f32 * player_hp_ratio) as i32;
            game.enemies = vec![
                // Main clearing — easy enemies near start
                Enemy::new_hollow_soldier(2, 350.0, 150.0),
                Enemy::new_hollow_soldier(3, 400.0, 300.0),
                Enemy::new_archer(4, 420.0, 200.0),
                // Side path — assassin ambush
                Enemy::new_assassin(5, 1000.0, 250.0),
                Enemy::new_hollow_soldier(6, 850.0, 350.0),
                // Forest path south — dense patrol
                Enemy::new_hollow_soldier(7, 400.0, 550.0),
                Enemy::new_knight(8, 500.0, 650.0),
                Enemy::new_archer(9, 450.0, 750.0),
                Enemy::new_assassin(10, 550.0, 850.0),
                // Wide forest area — mixed group
                Enemy::new_dark_mage(11, 800.0, 1000.0),
                Enemy::new_knight(12, 650.0, 1100.0),
                Enemy::new_hollow_soldier(13, 750.0, 1200.0),
                Enemy::new_archer(14, 900.0, 1250.0),
                // Near boss arena — tough guards
                Enemy::new_knight(15, 700.0, 1450.0),
                Enemy::new_dark_mage(16, 850.0, 1500.0),
            ];
            game.items = vec![
                // Main clearing
                WorldItem { x: 300.0, y: 250.0, kind: ItemKind::SoulOrb(200), collected: false },
                WorldItem { x: 450.0, y: 400.0, kind: ItemKind::EstusShard, collected: false },
                // Side path rewards
                WorldItem { x: 950.0, y: 200.0, kind: ItemKind::SoulOrb(300), collected: false },
                WorldItem { x: 950.0, y: 250.0, kind: ItemKind::PurpleMoss, collected: false },
                // Forest path
                WorldItem { x: 500.0, y: 600.0, kind: ItemKind::SoulOrb(200), collected: false },
                WorldItem { x: 550.0, y: 900.0, kind: ItemKind::HomewardBone, collected: false },
                // Deep forest
                WorldItem { x: 700.0, y: 1100.0, kind: ItemKind::SoulOrb(400), collected: false },
                WorldItem { x: 800.0, y: 1350.0, kind: ItemKind::PurpleMoss, collected: false },
                // Near boss arena
                WorldItem { x: 850.0, y: 1550.0, kind: ItemKind::SoulOrb(800), collected: false },
                WorldItem { x: 600.0, y: 1500.0, kind: ItemKind::EstusShard, collected: false },
            ];
            game.chests = vec![
                // Side path
                TreasureChest { x: 1050.0, y: 200.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::Dagger), is_mimic: false, mimic_revealed: false },
                // Forest path
                TreasureChest { x: 500.0, y: 700.0, opened: false, loot: ItemKind::ArmorDrop(ArmorSlot::Head, "Hollow Soldier Helm".into()), is_mimic: false, mimic_revealed: false },
                // Deep forest
                TreasureChest { x: 750.0, y: 1200.0, opened: false, loot: ItemKind::ArmorDrop(ArmorSlot::Chest, "Hollow Soldier Armor".into()), is_mimic: true, mimic_revealed: false },
                // Near boss arena
                TreasureChest { x: 900.0, y: 1600.0, opened: false, loot: ItemKind::RingDrop("Life Ring".into()), is_mimic: false, mimic_revealed: false },
                TreasureChest { x: 650.0, y: 1550.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::Spear), is_mimic: false, mimic_revealed: false },
            ];
            game.npcs = vec![
                Npc { x: 250.0, y: 150.0, name: "商人".into(), color: [0.8, 0.7, 0.3, 1.0],
                    dialogue: vec!["嘘！过来！".into(), "我有聚落里的好东西。".into(),
                        "[Enter] 购买紫苔藓 (200灵魂)".into()],
                    dialogue_index: 0, talking: false, kind: NpcKind::Merchant },
            ];
            game.lights = vec![
                Light { x: 200.0, y: 200.0, radius: 250.0, color: [0.7, 0.85, 0.5], intensity: 0.35 },
                Light { x: 1000.0, y: 300.0, radius: 180.0, color: [0.8, 0.7, 0.4], intensity: 0.15 },
                Light { x: 500.0, y: 400.0, radius: 200.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
                Light { x: 500.0, y: 700.0, radius: 200.0, color: [0.8, 0.5, 0.2], intensity: 0.2 },
                Light { x: 750.0, y: 1000.0, radius: 180.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
                Light { x: 900.0, y: 1300.0, radius: 200.0, color: [0.9, 0.5, 0.2], intensity: 0.15 },
                Light { x: 800.0, y: 1550.0, radius: 220.0, color: [0.8, 0.2, 0.4], intensity: 0.25 },
            ];
            game.bonfire_x = 200.0;
            game.bonfire_y = 200.0;
            let boss_defeated = game.bosses_defeated.iter().any(|b| b == "CurseRottedGreatwood");
            game.fog_gates = vec![
                FogGate { x: 200.0, y: 100.0, w: 80.0, h: 32.0, destination: AreaId::FirelinkShrine, dest_x: 500.0, dest_y: 350.0, active: true },
                FogGate { x: 600.0, y: 1350.0, w: 64.0, h: 80.0, destination: AreaId::CathedralDeep, dest_x: 200.0, dest_y: 200.0, active: true },
                // Boss fog gate at arena north entrance
                FogGate { x: 800.0, y: 1416.0, w: 128.0, h: 32.0, destination: AreaId::UndeadSettlement, dest_x: 800.0, dest_y: 1520.0, active: !boss_defeated },
            ];
        }
        AreaId::CathedralDeep => {
            // Cathedral of the Deep: wide stone causeways, towering structures
            // Layout: entrance causeway → knight patrol → great cathedral → boss arena
            let mut chunk = Chunk::new((0, 0));
            for y in 0..CHUNK_SIZE { for x in 0..CHUNK_SIZE { chunk.tiles[y][x] = TileId::Wall; } }
            // Entrance causeway (narrow path over water)
            for y in 15..25 { for x in 3..25 { chunk.tiles[y][x] = TileId::Ground; } }
            // First platform (knight patrol area)
            for y in 10..35 { for x in 22..50 { chunk.tiles[y][x] = TileId::Ground; } }
            // Long causeway east
            for y in 18..28 { for x in 45..80 { chunk.tiles[y][x] = TileId::Ground; } }
            // Second platform (Old Knight area)
            for y in 5..40 { for x in 75..105 { chunk.tiles[y][x] = TileId::Ground; } }
            // Cathedral approach
            for y in 25..50 { for x in 70..100 { chunk.tiles[y][x] = TileId::Ground; } }
            // Side path (hidden items)
            for y in 35..50 { for x in 40..65 { chunk.tiles[y][x] = TileId::Ground; } }
            // Boss arena (enclosed room with north door)
            // Room interior: y:55..75, x:65..95
            for y in 55..75 { for x in 65..95 { chunk.tiles[y][x] = TileId::Ground; } }
            // North wall with door gap (x:75..85 = opening)
            for x in 65..75 { chunk.tiles[54][x] = TileId::Wall; }
            for x in 85..95 { chunk.tiles[54][x] = TileId::Wall; }
            // South wall (solid)
            for x in 65..95 { chunk.tiles[75][x] = TileId::Wall; }
            // West wall (solid)
            for y in 54..76 { chunk.tiles[y][64] = TileId::Wall; }
            // East wall (solid)
            for y in 54..76 { chunk.tiles[y][95] = TileId::Wall; }
            // Shallow water channels
            for y in 12..18 { for x in 10..20 { chunk.tiles[y][x] = TileId::Poison; } }
            for y in 28..35 { for x in 50..70 { chunk.tiles[y][x] = TileId::Poison; } }

            game.chunk = chunk;
            game.collision = CollisionGrid::from_chunk(&game.chunk, &game.tileset);
            game.nav_grid = NavGrid::from_collision_grid(&game.collision, CHUNK_SIZE, 2);
            game.player.transform.x = 400.0;
            game.player.transform.y = 400.0;
            game.player.hp = (game.player.max_hp as f32 * player_hp_ratio) as i32;
            game.enemies = vec![
                // Entrance causeway
                Enemy::new_knight(2, 500.0, 300.0),
                // First platform — Old Knight patrol
                Enemy::new_knight(3, 700.0, 250.0),
                Enemy::new_archer(4, 600.0, 400.0),
                // Long causeway — archer ambush
                Enemy::new_archer(5, 1000.0, 350.0),
                // Second platform — heavy knight guard
                Enemy::new_knight(6, 1400.0, 200.0),
                Enemy::new_knight(7, 1500.0, 400.0),
                Enemy::new_dark_mage(8, 1300.0, 300.0),
                // Cathedral approach
                Enemy::new_knight(9, 1150.0, 600.0),
                Enemy::new_archer(10, 1300.0, 700.0),
                // Side path guard
                Enemy::new_assassin(11, 800.0, 650.0),
                // Mini-boss (Old Royal Knight)
                Enemy::new_mini_boss(12, 1100.0, 900.0),
            ];
            game.items = vec![
                // Entrance
                WorldItem { x: 300.0, y: 250.0, kind: ItemKind::SoulOrb(200), collected: false },
                // First platform
                WorldItem { x: 600.0, y: 350.0, kind: ItemKind::SoulOrb(300), collected: false },
                // Side path (hidden)
                WorldItem { x: 700.0, y: 700.0, kind: ItemKind::EstusShard, collected: false },
                WorldItem { x: 850.0, y: 650.0, kind: ItemKind::PurpleMoss, collected: false },
                // Cathedral area
                WorldItem { x: 1200.0, y: 550.0, kind: ItemKind::SoulOrb(500), collected: false },
                WorldItem { x: 1350.0, y: 600.0, kind: ItemKind::HomewardBone, collected: false },
                // Near boss arena
                WorldItem { x: 1100.0, y: 850.0, kind: ItemKind::SoulOrb(1000), collected: false },
            ];
            game.chests = vec![
                TreasureChest { x: 500.0, y: 320.0, opened: false, loot: ItemKind::SoulOrb(500), is_mimic: false, mimic_revealed: false },
                TreasureChest { x: 800.0, y: 700.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::Uchigatana), is_mimic: false, mimic_revealed: false },
                TreasureChest { x: 1500.0, y: 350.0, opened: false, loot: ItemKind::ArmorDrop(ArmorSlot::Chest, "Knight Armor".into()), is_mimic: true, mimic_revealed: false },
                TreasureChest { x: 1100.0, y: 950.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::GreatAxe), is_mimic: false, mimic_revealed: false },
            ];
            game.npcs = vec![];
            game.lights = vec![
                // Entrance (bonfire glow)
                Light { x: 400.0, y: 400.0, radius: 250.0, color: [0.9, 0.8, 0.6], intensity: 0.4 },
                // First platform
                Light { x: 600.0, y: 300.0, radius: 200.0, color: [0.5, 0.5, 0.8], intensity: 0.2 },
                // Causeway
                Light { x: 1000.0, y: 350.0, radius: 150.0, color: [0.5, 0.5, 0.8], intensity: 0.15 },
                // Second platform
                Light { x: 1400.0, y: 300.0, radius: 200.0, color: [0.5, 0.5, 0.8], intensity: 0.2 },
                // Cathedral approach
                Light { x: 1100.0, y: 650.0, radius: 180.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
                // Boss arena
                Light { x: 1300.0, y: 1000.0, radius: 250.0, color: [0.8, 0.2, 0.4], intensity: 0.25 },
            ];
            game.bonfire_x = 400.0;
            game.bonfire_y = 400.0;
            let dragonrider_defeated = game.bosses_defeated.iter().any(|b| b == "DeaconsOfTheDeep");
            game.fog_gates = vec![
                FogGate { x: 80.0, y: 320.0, w: 64.0, h: 80.0, destination: AreaId::FirelinkShrine, dest_x: 380.0, dest_y: 600.0, active: true },
                FogGate { x: 1550.0, y: 300.0, w: 64.0, h: 80.0, destination: AreaId::Irithyll, dest_x: 200.0, dest_y: 200.0, active: true },
                // Boss fog gate at arena north entrance
                FogGate { x: 1280.0, y: 856.0, w: 128.0, h: 32.0, destination: AreaId::CathedralDeep, dest_x: 1280.0, dest_y: 1040.0, active: !dragonrider_defeated },
            ];
        }
        AreaId::Irithyll => {
            // Fortress prison — tight corridors, many enemies, traps
            let mut chunk = Chunk::new((0, 0));
            for y in 0..CHUNK_SIZE { for x in 0..CHUNK_SIZE { chunk.tiles[y][x] = TileId::Wall; } }
            // Entry hall
            for y in 5..20 { for x in 5..40 { chunk.tiles[y][x] = TileId::Ground; } }
            // Main corridor
            for y in 20..30 { for x in 15..50 { chunk.tiles[y][x] = TileId::Ground; } }
            // Cell block 1
            for y in 30..55 { for x in 5..45 { chunk.tiles[y][x] = TileId::Ground; } }
            // Connecting hall
            for y in 35..45 { for x in 45..70 { chunk.tiles[y][x] = TileId::Ground; } }
            // Cell block 2
            for y in 45..75 { for x in 50..90 { chunk.tiles[y][x] = TileId::Ground; } }
            // Lower corridor
            for y in 75..85 { for x in 40..80 { chunk.tiles[y][x] = TileId::Ground; } }
            // Boss arena (enclosed room with north door)
            // Room interior: y:90..110, x:40..80
            for y in 90..110 { for x in 40..80 { chunk.tiles[y][x] = TileId::Ground; } }
            // North wall with door gap (x:52..62 = opening)
            for x in 40..52 { chunk.tiles[89][x] = TileId::Wall; }
            for x in 62..80 { chunk.tiles[89][x] = TileId::Wall; }
            // South wall (solid)
            for x in 40..80 { chunk.tiles[110][x] = TileId::Wall; }
            // West wall (solid)
            for y in 89..111 { chunk.tiles[y][39] = TileId::Wall; }
            // East wall (solid)
            for y in 89..111 { chunk.tiles[y][80] = TileId::Wall; }
            // Poison trap rooms
            for y in 55..65 { for x in 10..20 { chunk.tiles[y][x] = TileId::Poison; } }
            for y in 60..68 { for x in 75..85 { chunk.tiles[y][x] = TileId::Poison; } }

            game.chunk = chunk;
            game.collision = CollisionGrid::from_chunk(&game.chunk, &game.tileset);
            game.nav_grid = NavGrid::from_collision_grid(&game.collision, CHUNK_SIZE, 2);
            game.player.transform.x = 200.0;
            game.player.transform.y = 200.0;
            game.player.hp = (game.player.max_hp as f32 * player_hp_ratio) as i32;
            game.enemies = vec![
                Enemy::new_hollow_soldier(2, 300.0, 150.0),
                Enemy::new_archer(3, 450.0, 200.0),
                Enemy::new_hollow_soldier(4, 350.0, 350.0),
                Enemy::new_assassin(5, 200.0, 500.0),
                Enemy::new_dark_mage(6, 600.0, 450.0),
                Enemy::new_knight(7, 500.0, 600.0),
                Enemy::new_assassin(8, 700.0, 550.0),
                Enemy::new_hollow_soldier(9, 650.0, 700.0),
                Enemy::new_archer(10, 800.0, 650.0),
                Enemy::new_knight(11, 850.0, 800.0),
                Enemy::new_dark_mage(12, 850.0, 900.0),
                Enemy::new_hollow_soldier(14, 900.0, 1000.0),
                Enemy::new_knight(15, 950.0, 1100.0),
            ];
            game.items = vec![
                // Entry hall
                WorldItem { x: 250.0, y: 300.0, kind: ItemKind::SoulOrb(300), collected: false },
                WorldItem { x: 350.0, y: 400.0, kind: ItemKind::HomewardBone, collected: false },
                // Cell block 1
                WorldItem { x: 500.0, y: 500.0, kind: ItemKind::EstusShard, collected: false },
                WorldItem { x: 300.0, y: 600.0, kind: ItemKind::SoulOrb(200), collected: false },
                WorldItem { x: 200.0, y: 750.0, kind: ItemKind::PurpleMoss, collected: false },
                // Connecting hall / cell block 2
                WorldItem { x: 700.0, y: 650.0, kind: ItemKind::SoulOrb(500), collected: false },
                WorldItem { x: 900.0, y: 750.0, kind: ItemKind::PurpleMoss, collected: false },
                WorldItem { x: 1050.0, y: 900.0, kind: ItemKind::SoulOrb(800), collected: false },
                // Lower corridor / near boss
                WorldItem { x: 850.0, y: 1050.0, kind: ItemKind::SoulOrb(1500), collected: false },
                WorldItem { x: 700.0, y: 1250.0, kind: ItemKind::EstusShard, collected: false },
            ];
            game.chests = vec![
                TreasureChest { x: 300.0, y: 450.0, opened: false, loot: ItemKind::ArmorDrop(ArmorSlot::Chest, "Knight Armor".into()), is_mimic: false, mimic_revealed: false },
                TreasureChest { x: 650.0, y: 600.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::Spear), is_mimic: false, mimic_revealed: false },
                TreasureChest { x: 850.0, y: 850.0, opened: false, loot: ItemKind::RingDrop("Chloranthy Ring".into()), is_mimic: false, mimic_revealed: false },
                TreasureChest { x: 900.0, y: 1100.0, opened: false, loot: ItemKind::ArmorDrop(ArmorSlot::Head, "Knight Helm".into()), is_mimic: true, mimic_revealed: false },
                TreasureChest { x: 1000.0, y: 1250.0, opened: false, loot: ItemKind::WeaponDrop(crate::combat::weapon::WeaponType::Uchigatana), is_mimic: false, mimic_revealed: false },
            ];
            game.npcs = vec![];
            game.lights = vec![
                Light { x: 200.0, y: 200.0, radius: 200.0, color: [0.6, 0.6, 0.7], intensity: 0.3 },
                Light { x: 350.0, y: 200.0, radius: 120.0, color: [0.4, 0.3, 0.7], intensity: 0.15 },
                Light { x: 400.0, y: 350.0, radius: 150.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
                Light { x: 600.0, y: 500.0, radius: 180.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
                Light { x: 750.0, y: 700.0, radius: 180.0, color: [0.9, 0.6, 0.3], intensity: 0.15 },
                Light { x: 900.0, y: 900.0, radius: 200.0, color: [0.7, 0.4, 0.8], intensity: 0.2 },
                Light { x: 1000.0, y: 1100.0, radius: 180.0, color: [0.5, 0.5, 0.6], intensity: 0.15 },
                Light { x: 800.0, y: 1350.0, radius: 220.0, color: [0.3, 0.3, 0.8], intensity: 0.25 },
            ];
            game.bonfire_x = 200.0;
            game.bonfire_y = 200.0;
            let boss_defeated = game.bosses_defeated.iter().any(|b| b == "PontiffSulyvahn");
            game.fog_gates = vec![
                FogGate { x: 80.0, y: 100.0, w: 64.0, h: 80.0, destination: AreaId::CathedralDeep, dest_x: 1700.0, dest_y: 400.0, active: true },
                // Boss fog gate at arena north entrance
                FogGate { x: 912.0, y: 1416.0, w: 128.0, h: 32.0, destination: AreaId::Irithyll, dest_x: 912.0, dest_y: 1520.0, active: !boss_defeated },
            ];
        }
    }

    // Pre-spawn boss at arena center if area has a boss and not yet defeated
    game.boss = None;
    game.boss_active = false;
    game.boss_defeated = false;
    if let Some(boss_type) = area_boss(area) {
        let boss_name = match boss_type {
            BossType::IudexGundyr => "IudexGundyr",
            BossType::Vordt => "Vordt",
            BossType::DemonKnight => "CurseRottedGreatwood",
            BossType::Dragonrider => "DeaconsOfTheDeep",
            BossType::RuinSentinel => "PontiffSulyvahn",
        };
        let already_defeated = game.bosses_defeated.iter().any(|b| b == boss_name);
        if !already_defeated {
            let (cx, cy) = match area {
                AreaId::CemeteryOfAsh => (1540.0, 470.0),
                AreaId::LothricWall => (960.0, 1500.0),
                AreaId::UndeadSettlement => (960.0, 1600.0),
                AreaId::CathedralDeep => (1280.0, 1040.0),
                AreaId::Irithyll => (960.0, 1600.0),
                _ => (400.0, 400.0),
            };
            let boss = match boss_type {
                BossType::IudexGundyr => crate::entity::boss::Boss::new_iudex_gundyr(100, cx, cy),
                BossType::Vordt => crate::entity::boss::Boss::new_vordt(100, cx, cy),
                BossType::DemonKnight => crate::entity::boss::Boss::new_test_boss(100, cx, cy),
                BossType::Dragonrider => crate::entity::boss::Boss::new_dragonrider(100, cx, cy),
                BossType::RuinSentinel => crate::entity::boss::Boss::new_ruin_sentinel(100, cx, cy),
            };
            game.boss = Some(boss);
        }
    }
    // Mark boss as defeated for current area (for fog gate deactivation)
    if let Some(boss_type) = area_boss(area) {
        let boss_name = match boss_type {
            BossType::IudexGundyr => "IudexGundyr",
            BossType::Vordt => "Vordt",
            BossType::DemonKnight => "CurseRottedGreatwood",
            BossType::Dragonrider => "DeaconsOfTheDeep",
            BossType::RuinSentinel => "PontiffSulyvahn",
        };
        if game.bosses_defeated.iter().any(|b| b == boss_name) {
            game.boss_defeated = true;
        }
    }
    // New Game+ difficulty scaling: enemies gain +40% HP and +30% damage per cycle
    if game.ng_plus > 0 {
        let hp_mult = 1.0 + 0.4 * game.ng_plus as f32;
        let dmg_mult = 1.0 + 0.3 * game.ng_plus as f32;
        for enemy in &mut game.enemies {
            enemy.max_hp = (enemy.max_hp as f32 * hp_mult) as i32;
            enemy.hp = enemy.max_hp;
            enemy.damage = (enemy.damage as f32 * dmg_mult) as i32;
        }
        if let Some(ref mut boss) = game.boss {
            boss.max_hp = (boss.max_hp as f32 * hp_mult) as i32;
            boss.hp = boss.max_hp;
            boss.damage = (boss.damage as f32 * dmg_mult) as i32;
        }
    }
    game.camera.x = game.player.transform.x;
    game.camera.y = game.player.transform.y;
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

fn update_travel_menu(game: &mut Game) {
    if game.input.consume_pressed(KeyCode::Escape) {
        game.state = GameState::BonfireMenu;
        game.menu = MenuState::bonfire_menu();
        return;
    }
    if game.input.pressed(KeyCode::Up) {
        game.menu.move_up();
    }
    if game.input.pressed(KeyCode::Down) {
        game.menu.move_down();
    }
    if game.input.consume_pressed(KeyCode::Enter) {
        let idx = game.menu.selected_index;
        let areas = [AreaId::FirelinkShrine, AreaId::LothricWall, AreaId::UndeadSettlement, AreaId::CathedralDeep, AreaId::Irithyll];
        if idx < 5 {
            load_area(game, areas[idx]);
        } else {
            // Back
            game.state = GameState::BonfireMenu;
            game.menu = MenuState::bonfire_menu();
        }
    }
}

fn update_victory(game: &mut Game) {
    if game.input.consume_pressed(KeyCode::Enter) {
        // Start New Game+ — keep level and stats, increase difficulty
        game.ng_plus += 1;
        game.player.hp = game.player.max_hp;
        game.boss_defeated = false;
        game.boss_active = false;
        game.boss = None;
        game.souls = 0;
        game.bosses_defeated = vec![];
        game.enemies_killed = 0;
        game.damage_dealt = 0;
        game.damage_taken = 0;
        game.death_count = 0;
        game.play_time = 0.0;
        game.inventory = vec![];
        game.has_bloodstain = false;
        game.bloodstain_souls = 0;
        game.time.accumulator = 0.0;
        game.state_timer = 0.0;
        load_area(game, AreaId::FirelinkShrine);
        game.state = GameState::Playing;
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
    if area_has_bonfire(game.area) {
        // Warm glow aura (pulsing)
        let pulse = (game.time.accumulator as f32 * 1.5).sin() * 0.15 + 0.85;
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

    // --- Draw fog gates as doorways ---
    {
        let pulse = (game.time.accumulator as f32 * 1.2).sin() * 0.1 + 0.9;
        for gate in &game.fog_gates {
            if !gate.active { continue; }
            let is_boss = gate.destination == game.area;
            let is_vertical = gate.h > gate.w;
            let (frame_color, fog_color) = if is_boss {
                ([0.5f32, 0.3, 0.1, 1.0], [0.5, 0.2, 0.7, 0.5 * pulse])
            } else {
                ([0.4f32, 0.35, 0.25, 1.0], [0.3, 0.5, 0.7, 0.35 * pulse])
            };
            if is_vertical {
                // Vertical doorway — two pillars + fog between
                let pillar_w = 8.0;
                let pillar_h = gate.h;
                // Left pillar
                game.batcher.draw(
                    InstanceData::new(gate.x - gate.w * 0.5 - pillar_w * 0.5, gate.y, pillar_w, pillar_h, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                // Right pillar
                game.batcher.draw(
                    InstanceData::new(gate.x + gate.w * 0.5 + pillar_w * 0.5, gate.y, pillar_w, pillar_h, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                // Fog fill between pillars
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y, gate.w, gate.h, [0.0, 0.0, 1.0, 1.0], fog_color),
                    &game.white_tex, gl,
                );
                // Arch at top
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y - gate.h * 0.5 - 3.0, gate.w + pillar_w * 2.0, 6.0, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
            } else {
                // Horizontal doorway — two pillars + fog
                let pillar_w = gate.w;
                let pillar_h = 8.0;
                // Top pillar
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y - gate.h * 0.5 - pillar_h * 0.5, pillar_w, pillar_h, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                // Bottom pillar
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y + gate.h * 0.5 + pillar_h * 0.5, pillar_w, pillar_h, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                // Fog fill
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y, gate.w, gate.h, [0.0, 0.0, 1.0, 1.0], fog_color),
                    &game.white_tex, gl,
                );
                // Side pillars
                game.batcher.draw(
                    InstanceData::new(gate.x - gate.w * 0.5 - 3.0, gate.y, 6.0, gate.h + pillar_h * 2.0, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                game.batcher.draw(
                    InstanceData::new(gate.x + gate.w * 0.5 + 3.0, gate.y, 6.0, gate.h + pillar_h * 2.0, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
            }
        }
    }

    // --- Draw wall torches (at light positions, skip player light [0] and bonfire light [1]) ---
    for i in 2..game.lights.len() {
        let light = &game.lights[i];
        let flicker = (game.time.accumulator as f32 * (3.0 + i as f32 * 0.7)).sin() * 0.2 + 0.8;
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
            ItemKind::ArmorDrop(_, _) => (0.5, 0.5, 0.8),
            ItemKind::RingDrop(_) => (0.9, 0.8, 0.2),
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
        if chest.mimic_revealed { continue; } // Mimic is now rendered as an enemy
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
        let pulse = (game.time.accumulator as f32).sin() * 0.3 + 0.7;
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
        let (body_w, body_h, head_size) = match npc.kind {
            NpcKind::Blacksmith => (24.0, 28.0, 12.0), // Stocky
            NpcKind::Merchant => (20.0, 24.0, 10.0),   // Thin
            NpcKind::LevelUp => (22.0, 30.0, 11.0),    // Tall
            _ => (22.0, 26.0, 10.0),
        };
        // Body
        game.batcher.draw(
            InstanceData::new(npc.x, npc.y + bob, body_w, body_h, [0.0, 0.0, 1.0, 1.0], npc.color),
            &game.white_tex, gl,
        );
        // Head (lighter shade)
        let head_color = [
            (npc.color[0] + 0.3).min(1.0),
            (npc.color[1] + 0.3).min(1.0),
            (npc.color[2] + 0.3).min(1.0),
            1.0,
        ];
        game.batcher.draw(
            InstanceData::new(npc.x, npc.y - body_h * 0.5 - head_size * 0.5 + bob, head_size, head_size, [0.0, 0.0, 1.0, 1.0], head_color),
            &game.white_tex, gl,
        );
        // Interact indicator when nearby
        let proximity = {
            let dx = game.player.transform.x - npc.x;
            let dy = game.player.transform.y - npc.y;
            (dx * dx + dy * dy).sqrt() < 50.0
        };
        if proximity {
            let flash = (game.play_time * 4.0).sin() * 0.3 + 0.7;
            game.batcher.draw(
                InstanceData::new(npc.x, npc.y - body_h * 0.5 - head_size - 6.0, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.0, flash]),
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
        if !boss.is_dead() && boss.boss_activated {
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

    // --- Lock-on indicator (diamond above locked target) ---
    if let Some((tx, ty)) = game.lock_on_pos {
        let pulse = 0.8 + (game.state_timer * 6.0).sin() * 0.2;
        let size = 12.0 * pulse;
        let ly = ty - 30.0;
        // Diamond shape: rotate 45 degrees
        let angle = game.state_timer * 2.0;
        let dx1 = angle.cos() * size * 0.5;
        let dy1 = angle.sin() * size * 0.5;
        game.batcher.draw(
            InstanceData::new(tx + dx1, ly + dy1, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 0.8, 0.2, 0.9]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(tx - dy1, ly + dx1, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 0.8, 0.2, 0.9]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(tx - dx1, ly - dy1, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 0.8, 0.2, 0.9]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(tx + dy1, ly - dx1, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 0.8, 0.2, 0.9]),
            &game.white_tex, gl,
        );
    }

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
        let total = if game.player.is_heavy_attack { game.player.heavy_attack_duration() } else { game.player.light_attack_duration() };
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
        let pulse = (game.time.accumulator as f32 * 2.0).sin() * 0.1 + 0.15;
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
        if !boss.is_dead() && boss.boss_activated {
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

    // --- Equipment Slot UI (bottom-left, DS3 cross layout) ---
    {
        let slot_size = 40.0;
        let gap = 4.0;
        let base_x = 30.0 + slot_size + gap;
        let base_y = game.screen_h - 30.0 - slot_size - gap;

        // Background helper: draws a slot box with dark fill and border
        let bg_color = [0.08f32, 0.08, 0.08, 0.85];
        let border_color = [0.35f32, 0.3, 0.25, 0.9];

        // Cross layout centered at (base_x, base_y)
        let spell_x = base_x;
        let spell_y = base_y - slot_size - gap; // visual top
        let item_x = base_x;
        let item_y = base_y + slot_size + gap;  // visual bottom
        let left_x = base_x - slot_size - gap;
        let left_y = base_y;
        let right_x = base_x + slot_size + gap;
        let right_y = base_y;

        // Helper closure to draw a slot
        let draw_slot = |gl: &GL, x: f32, y: f32| {
            game.ui_renderer.draw_bar(gl, x, y, slot_size, slot_size, 1.0, bg_color, bg_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, x, y - slot_size * 0.5, slot_size, 1.5, 1.0, border_color, border_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, x, y + slot_size * 0.5, slot_size, 1.5, 1.0, border_color, border_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, x - slot_size * 0.5, y, 1.5, slot_size, 1.0, border_color, border_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, x + slot_size * 0.5, y, 1.5, slot_size, 1.0, border_color, border_color, &ui_proj);
        };

        draw_slot(gl, spell_x, spell_y);
        draw_slot(gl, item_x, item_y);
        draw_slot(gl, left_x, left_y);
        draw_slot(gl, right_x, right_y);

        // --- Icons inside slots ---
        let icon_dim = [0.0f32, 0.0, 1.0, 1.0];

        // Spell slot icon (top in screen = spell_y, smallest Y): dim diamond
        let spell_dim = [0.25f32, 0.2, 0.35, 0.5];
        game.ui_renderer.draw_bar(gl, spell_x, spell_y, 14.0, 14.0, 1.0, icon_dim, spell_dim, &ui_proj);
        game.ui_renderer.draw_bar(gl, spell_x, spell_y - 3.0, 8.0, 8.0, 1.0, spell_dim, spell_dim, &ui_proj);
        game.ui_renderer.draw_bar(gl, spell_x, spell_y + 3.0, 8.0, 8.0, 1.0, spell_dim, spell_dim, &ui_proj);

        // Item slot icon (bottom in screen = item_y, largest Y): gold flask (estus)
        let flask_color = [0.9f32, 0.7, 0.1, 0.8];
        game.ui_renderer.draw_bar(gl, item_x, item_y + 2.0, 12.0, 16.0, 1.0, icon_dim, flask_color, &ui_proj);
        game.ui_renderer.draw_bar(gl, item_x, item_y - 8.0, 6.0, 6.0, 1.0, icon_dim, flask_color, &ui_proj);
        let cap_color = [0.7f32, 0.5, 0.2, 0.8];
        game.ui_renderer.draw_bar(gl, item_x, item_y - 12.0, 8.0, 3.0, 1.0, icon_dim, cap_color, &ui_proj);

        // Left slot icon: shield shape
        let is_shield = game.player.equipment.left_hand.active().weapon_type == crate::combat::weapon::WeaponType::Shield;
        if is_shield {
            let shield_color = [0.3f32, 0.5, 0.8, 0.8];
            game.ui_renderer.draw_bar(gl, left_x, left_y, 18.0, 22.0, 1.0, icon_dim, shield_color, &ui_proj);
            let cross_color = [0.9f32, 0.8, 0.3, 0.9];
            game.ui_renderer.draw_bar(gl, left_x, left_y, 2.0, 14.0, 1.0, icon_dim, cross_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, left_x, left_y - 2.0, 12.0, 2.0, 1.0, icon_dim, cross_color, &ui_proj);
        } else {
            // Weapon icon (small blade)
            let wep_color = [0.6f32, 0.6, 0.65, 0.8];
            game.ui_renderer.draw_bar(gl, left_x, left_y - 4.0, 3.0, 20.0, 1.0, icon_dim, wep_color, &ui_proj);
            let guard_color = [0.5f32, 0.35, 0.2, 0.9];
            game.ui_renderer.draw_bar(gl, left_x, left_y + 6.0, 12.0, 3.0, 1.0, icon_dim, guard_color, &ui_proj);
        }

        // Right slot icon: sword shape
        let sword_color = [0.75f32, 0.75, 0.8, 0.85];
        // Blade
        game.ui_renderer.draw_bar(gl, right_x, right_y - 4.0, 3.0, 20.0, 1.0, icon_dim, sword_color, &ui_proj);
        // Cross-guard
        let guard_color2 = [0.5f32, 0.35, 0.2, 0.9];
        game.ui_renderer.draw_bar(gl, right_x, right_y + 6.0, 14.0, 3.0, 1.0, icon_dim, guard_color2, &ui_proj);
        // Pommel
        let pommel_color = [0.4f32, 0.3, 0.2, 0.8];
        game.ui_renderer.draw_bar(gl, right_x, right_y + 14.0, 5.0, 5.0, 1.0, icon_dim, pommel_color, &ui_proj);
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
        if area_has_bonfire(game.area) {
            let bfx = map_left + game.bonfire_x * scale;
            let bfy = map_top + game.bonfire_y * scale;
            game.ui_renderer.draw_bar(
                gl, bfx, bfy, 4.0, 4.0,
                1.0, [1.0, 0.7, 0.2, 1.0], [1.0, 0.7, 0.2, 1.0], &ui_proj,
            );
        }
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
        if matches!(game.state, GameState::TitleScreen | GameState::DeathScreen | GameState::BonfireMenu | GameState::LevelUpMenu | GameState::TravelMenu) {
            let header = if game.state == GameState::LevelUpMenu {
                format!("<div class=\"menu-item\" style=\"color:#aaa;font-size:16px\">等级 {} · 灵魂: {} · 费用: {}</div>", game.player.level, game.souls, game.player.level_up_cost())
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
                el.set_text_content(Some("你死了"));
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
            let bosses_list = game.bosses_defeated.join(", ");
            let ng_label = if game.ng_plus == 0 { String::new() } else { format!("NG+{} ", game.ng_plus) };
            el.set_text_content(Some(&format!(
                "胜利\n\n{}火焰已传承。\n\n已击败Boss: {}\n用时: {}:{:02}\n击杀敌人: {}\n造成伤害: {}\n承受伤害: {}\n死亡次数: {}\n等级: {}\n\n按Enter开始新周目",
                ng_label, bosses_list, mins, secs, game.enemies_killed, game.damage_dealt, game.damage_taken, game.death_count, game.player.level
            )));
            let _ = el.set_attribute("style",
                "color: #e8c840; text-shadow: 0 0 30px rgba(232,200,64,0.8), 0 0 60px rgba(232,200,64,0.3); \
                 white-space: pre-line; letter-spacing: 4px; line-height: 1.6; font-size: 18px;");
        } else {
            let _ = el.set_attribute("style", "display:none");
        }
    }

    // Level-up flash text
    if let Some(el) = document.get_element_by_id("level-up-text") {
        if game.level_up_flash > 0.0 {
            let alpha = (game.level_up_flash / 1.5).min(1.0);
            let _ = el.set_attribute("style", &format!("opacity: {}; color: #e8c840; font-size: 32px; text-shadow: 0 0 20px rgba(232,200,64,0.8); letter-spacing: 8px;", alpha));
            el.set_text_content(Some(&format!("等级 {}", game.player.level)));
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
            EntityState::Idle => "待机",
            EntityState::Moving => "移动",
            EntityState::Attacking => "攻击",
            EntityState::Rolling => "翻滚",
            EntityState::Staggered => "硬直",
            EntityState::Dead => "死亡",
            EntityState::Blocking => "格挡",
        };
        let mut text = format!(
            "HP {}/{} | 精力 {}/{} | 攻击 {} | Lv{} | {} | {}",
            hp, max_hp, stamina, max_sta, game.player.damage(), game.player.level, state_name,
            game.player.weapon.name
        );
        // Bonfire proximity hint
        if game.state == GameState::Playing && area_has_bonfire(game.area) {
            let (px, py) = game.player.position();
            let dx = px - game.bonfire_x;
            let dy = py - game.bonfire_y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < 40.0 {
                text.push_str(" | [Enter] 篝火");
            }
            // Chest proximity hint
            for chest in &game.chests {
                if chest.opened || chest.mimic_revealed { continue; }
                let cdx = px - chest.x;
                let cdy = py - chest.y;
                let cdist = (cdx * cdx + cdy * cdy).sqrt();
                if cdist < 30.0 {
                    text.push_str(" | [Enter] 开启宝箱");
                    break;
                }
            }
            // NPC proximity hint
            for npc in &game.npcs {
                let ndx = px - npc.x;
                let ndy = py - npc.y;
                let ndist = (ndx * ndx + ndy * ndy).sqrt();
                if ndist < 40.0 {
                    text.push_str(&format!(" | [Enter] 与{}对话", npc.name));
                    break;
                }
            }
        }
        el.set_text_content(Some(&text));
    }

    // Souls + area name
    if let Some(el) = document.get_element_by_id("souls-text") {
        let mut text = format!("{}{} | 灵魂: {} | 原素瓶: {}/{}",
            if game.ng_plus > 0 { format!("NG+{} ", game.ng_plus) } else { String::new() },
            area_name(game.area), game.souls, game.bonfire.estus_charges, game.bonfire.estus_max);
        // Show consumable hint
        let has_moss = game.inventory.iter().any(|i| matches!(&i.kind, InventoryItemKind::Consumable(n) if n == "PurpleMoss"));
        let has_bone = game.inventory.iter().any(|i| matches!(&i.kind, InventoryItemKind::Consumable(n) if n == "HomewardBone"));
        if has_moss { text.push_str(" | [Q] 苔藓"); }
        if has_bone { text.push_str(" | [Q] 归骨"); }
        if game.player.poison_timer > 0.0 {
            text.push_str(&format!(" | 中毒 ({:.0}s)", game.player.poison_timer));
        }
        if let Some((ref msg, t)) = game.pickup_notification {
            let alpha = (t / 2.0).min(1.0);
            text.push_str(&format!("<br/><span style='color:#e8c840;opacity:{:.2}'>▲ {}</span>", alpha, msg));
            el.set_inner_html(&text);
        } else {
            el.set_text_content(Some(&text));
        }
        // Tint text when poisoned
        let style = if game.player.poison_timer > 0.0 { "color: #6c6;white-space:pre-line;" } else { "white-space:pre-line;" };
        let _ = el.set_attribute("style", style);
    }

    // Equipment slot labels removed — icons only
    if let Some(el) = document.get_element_by_id("equip-slots") {
        el.set_inner_html("");
    }

    // Inventory panel (I key to toggle)
    if let Some(el) = document.get_element_by_id("menu") {
        if game.show_inventory {
            let defense = game.player.equipment.total_defense();
            let weight = game.player.equipment.total_weight();
            let equip_load = game.player.equipment.equip_load_percent(40.0 + 10.0 * 1.5);
            let roll_type = if equip_load < 0.3 { "快速" } else if equip_load < 0.7 { "普通" } else { "缓慢" };

            let mut html = String::from("<div style='color:#e8c840;font-size:20px;text-align:center;margin-bottom:8px'>背包</div>");
            html.push_str(&format!("<div style='color:#aaa;font-size:14px'>防御: {:.0} | 负重: {:.1} | 翻滚: {}</div>", defense, weight, roll_type));
            html.push_str("<div style='color:#888;font-size:12px;margin:4px 0'>— 武器 —</div>");
            html.push_str(&format!("<div style='color:#ccc;font-size:13px'>右手: {}</div>", game.player.weapon.name));
            if let Some(ref alt) = game.player.alt_weapon {
                html.push_str(&format!("<div style='color:#999;font-size:13px'>备用: {} [1键切换]</div>", alt.name));
            }
            html.push_str("<div style='color:#888;font-size:12px;margin:4px 0'>— 装备 —</div>");
            html.push_str(&format!("<div style='color:#ccc;font-size:13px'>头部: {}</div>", game.player.equipment.head.name));
            html.push_str(&format!("<div style='color:#ccc;font-size:13px'>身体: {}</div>", game.player.equipment.chest.name));
            html.push_str(&format!("<div style='color:#ccc;font-size:13px'>戒指1: {}</div>", game.player.equipment.ring_1.as_ref().map_or("无", |r| &r.name)));
            html.push_str(&format!("<div style='color:#ccc;font-size:13px'>戒指2: {}</div>", game.player.equipment.ring_2.as_ref().map_or("无", |r| &r.name)));
            if !game.inventory.is_empty() {
                html.push_str("<div style='color:#888;font-size:12px;margin:4px 0'>— 物品 —</div>");
                for item in &game.inventory {
                    let desc = match &item.kind {
                        InventoryItemKind::Consumable(n) if n == "PurpleMoss" => " (Q使用: 治愈中毒)",
                        InventoryItemKind::Consumable(n) if n == "HomewardBone" => " (Q使用: 传送至篝火)",
                        _ => "",
                    };
                    html.push_str(&format!("<div style='color:#aaa;font-size:13px'>· {}{}</div>", item.name, desc));
                }
            }
            html.push_str("<div style='color:#666;font-size:12px;margin-top:8px'>按I关闭</div>");
            let _ = el.set_attribute("style", "display:block; background:rgba(0,0,0,0.9); padding:16px; border:1px solid #555; border-radius:4px; max-width:400px; margin:40px auto; white-space:pre-line;");
            el.set_text_content(None);
            el.set_inner_html(&html);
        }
    }

    // Boss name — only show when boss is activated
    if let Some(el) = document.get_element_by_id("boss-name") {
        if let Some(ref boss) = game.boss {
            if !boss.is_dead() && boss.boss_activated {
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

    // Minimap
    if game.state == GameState::Playing {
        if let Some(minimap_el) = document.get_element_by_id("minimap-canvas") {
            let canvas: web_sys::HtmlCanvasElement = match minimap_el.dyn_into::<web_sys::HtmlCanvasElement>() {
                Ok(c) => c,
                Err(_) => return,
            };
            let ctx = match canvas.get_context("2d").ok().flatten() {
                Some(ctx) => ctx.dyn_into::<web_sys::CanvasRenderingContext2d>().ok(),
                None => None,
            };
            if let Some(ctx) = ctx {
                #[allow(deprecated)]
                fn fill_style(ctx: &web_sys::CanvasRenderingContext2d, color: &str) {
                    ctx.set_fill_style(&color.into());
                }
                let mm_w = 120.0_f64;
                let mm_h = 120.0_f64;
                let scale_x = mm_w / (CHUNK_SIZE as f64 * TILE_SIZE as f64);
                let scale_y = mm_h / (CHUNK_SIZE as f64 * TILE_SIZE as f64);
                let scale = scale_x.min(scale_y);
                let (px, py) = game.player.position();

                ctx.clear_rect(0.0, 0.0, mm_w, mm_h);

                // Draw tiles (sample every 2 tiles for performance)
                for ty in (0..CHUNK_SIZE).step_by(2) {
                    for tx in (0..CHUNK_SIZE).step_by(2) {
                        let tile = game.chunk.tiles[ty][tx];
                        let color = match tile {
                            TileId::Ground => "#333",
                            TileId::Wall => "#1a1a1a",
                            TileId::Poison => "#2a3a1a",
                            _ => continue,
                        };
                        fill_style(&ctx, color);
                        let mx = tx as f64 * TILE_SIZE as f64 * scale;
                        let my = ty as f64 * TILE_SIZE as f64 * scale;
                        let s = 2.0 * TILE_SIZE as f64 * scale;
                        ctx.fill_rect(mx, my, s, s);
                    }
                }

                // Draw enemies as red dots
                fill_style(&ctx, "#c44");
                for enemy in &game.enemies {
                    if enemy.is_dead() { continue; }
                    let (ex, ey) = enemy.position();
                    ctx.begin_path();
                    let _ = ctx.arc(ex as f64 * scale, ey as f64 * scale, 2.0, 0.0, std::f64::consts::TAU);
                    ctx.fill();
                }

                // Draw boss as large red dot
                if let Some(ref boss) = game.boss {
                    if !boss.is_dead() {
                        fill_style(&ctx, "#f80");
                        let (bx, by) = boss.position();
                        ctx.begin_path();
                        let _ = ctx.arc(bx as f64 * scale, by as f64 * scale, 3.0, 0.0, std::f64::consts::TAU);
                        ctx.fill();
                    }
                }

                // Draw fog gates as blue bars
                fill_style(&ctx, "#48f");
                for gate in &game.fog_gates {
                    if !gate.active { continue; }
                    let gx = gate.x as f64 * scale;
                    let gy = gate.y as f64 * scale;
                    let gw = gate.w as f64 * scale;
                    let gh = gate.h as f64 * scale;
                    ctx.fill_rect(gx - gw * 0.5, gy - gh * 0.5, gw, gh);
                }

                // Draw player as bright dot
                fill_style(&ctx, "#0f0");
                ctx.begin_path();
                let _ = ctx.arc(px as f64 * scale, py as f64 * scale, 2.5, 0.0, std::f64::consts::TAU);
                ctx.fill();

                // Draw bonfire as yellow dot
                if area_has_bonfire(game.area) {
                    fill_style(&ctx, "#e8c840");
                    ctx.begin_path();
                    let _ = ctx.arc(game.bonfire_x as f64 * scale, game.bonfire_y as f64 * scale, 2.0, 0.0, std::f64::consts::TAU);
                    ctx.fill();
                }
            }
        }
    } else if let Some(minimap_el) = document.get_element_by_id("minimap-canvas") {
        let _ = minimap_el.set_attribute("style", "display:none");
    }
}
