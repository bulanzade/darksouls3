use crate::bridge::textures;
use crate::audio::audio_engine::AudioEngine;
use crate::core::camera::Camera2D;
use crate::core::input::InputState;
use crate::core::input::KeyCode;
use crate::core::time::{Time, FIXED_DT};
use crate::entity::boss::Boss;
use crate::entity::boss::BossType;
use crate::entity::enemy::Enemy;
use crate::entity::entity_trait::{DamageInfo, Entity, EntityId, EntityState};
use crate::entity::player::Player;
use crate::game::{GameState, MenuState};
use crate::render::gl_context::GlContext;
use crate::render::light_renderer::{Light, LightRenderer};
use crate::render::post_process::PostProcessor;
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use crate::render::ui_renderer::UiRenderer;
use crate::save::bonfire::BonfireState;
use crate::world::chunk::{Chunk, CHUNK_SIZE};
use crate::world::collision::CollisionGrid;
use crate::world::nav_grid::NavGrid;
use crate::world::tileset::{TileId, Tileset, TILE_SIZE};
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;

#[derive(Clone, Copy, PartialEq, Debug, Eq, Hash)]
pub(crate) enum AreaId {
    CemeteryOfAsh,
    FirelinkShrine,
    LothricWall,
    UndeadSettlement,
    CathedralDeep,
    Irithyll,
}

pub(crate) fn area_name(area: AreaId) -> &'static str {
    match area {
        AreaId::CemeteryOfAsh => "灰烬墓地",
        AreaId::FirelinkShrine => "传火祭祀场",
        AreaId::LothricWall => "洛斯里克高墙",
        AreaId::UndeadSettlement => "不死聚落",
        AreaId::CathedralDeep => "幽邃教堂",
        AreaId::Irithyll => "冷冽谷的伊鲁席尔",
    }
}

pub(crate) fn area_boss(area: AreaId) -> Option<BossType> {
    match area {
        AreaId::CemeteryOfAsh => Some(BossType::IudexGundyr),
        AreaId::LothricWall => Some(BossType::Vordt),
        AreaId::UndeadSettlement => Some(BossType::DemonKnight),
        AreaId::CathedralDeep => Some(BossType::Dragonrider),
        AreaId::Irithyll => Some(BossType::RuinSentinel),
        _ => None,
    }
}

pub(crate) fn boss_defeat_key(boss: BossType) -> &'static str {
    match boss {
        BossType::IudexGundyr => "IudexGundyr",
        BossType::Vordt => "Vordt",
        BossType::DemonKnight => "CurseRottedGreatwood",
        BossType::Dragonrider => "DeaconsOfTheDeep",
        BossType::RuinSentinel => "PontiffSulyvahn",
    }
}

pub(crate) fn area_has_bonfire(area: AreaId) -> bool {
    area != AreaId::CemeteryOfAsh
}

/// Stored area data — used to persist areas when switching between them
#[allow(dead_code)]
pub(crate) struct StoredArea {
    pub(crate) chunk: Chunk,
    pub(crate) collision: CollisionGrid,
    pub(crate) nav_grid: NavGrid,
    pub(crate) enemies: Vec<Enemy>,
    pub(crate) boss: Option<Boss>,
    pub(crate) items: Vec<WorldItem>,
    pub(crate) npcs: Vec<Npc>,
    pub(crate) chests: Vec<TreasureChest>,
    pub(crate) lights: Vec<Light>,
    pub(crate) fog_gates: Vec<FogGate>,
    pub(crate) bonfire_x: f32,
    pub(crate) bonfire_y: f32,
    pub(crate) boss_active: bool,
    pub(crate) boss_defeated: bool,
}

#[allow(dead_code)]
pub(crate) struct Game {
    pub(crate) gl_ctx: GlContext,
    pub(crate) batcher: SpriteBatcher,
    pub(crate) texture: Texture,
    pub(crate) player_tex: Texture,
    pub(crate) enemy_tex: Texture,
    pub(crate) boss_tex: Texture,
    pub(crate) white_tex: Texture,
    pub(crate) bonfire_tex: Texture,
    pub(crate) time: Time,
    pub(crate) input: InputState,
    pub(crate) camera: Camera2D,
    pub(crate) player: Player,
    pub(crate) enemies: Vec<Enemy>,
    pub(crate) boss: Option<Boss>,
    pub(crate) chunk: Chunk,
    pub(crate) tileset: Tileset,
    pub(crate) collision: CollisionGrid,
    pub(crate) nav_grid: NavGrid,
    pub(crate) tileset_texture: Texture,
    // Rendering subsystems
    pub(crate) light_renderer: LightRenderer,
    pub(crate) post_processor: PostProcessor,
    pub(crate) ui_renderer: UiRenderer,
    // Framebuffer for post-processing
    pub(crate) scene_fbo: web_sys::WebGlFramebuffer,
    pub(crate) scene_texture: web_sys::WebGlTexture,
    // Secondary chunk for seamless neighbor rendering
    pub(crate) neighbor_chunk: Option<(AreaId, Chunk, CollisionGrid)>,
    // Lights
    pub(crate) lights: Vec<Light>,
    // Game state
    pub(crate) state: GameState,
    pub(crate) menu: MenuState,
    // RPG
    pub(crate) souls: u32,
    pub(crate) bonfire: BonfireState,
    pub(crate) audio: AudioEngine,
    // Boss tracking
    pub(crate) boss_active: bool,
    pub(crate) boss_defeated: bool,
    // Lock-on targeting
    pub(crate) lock_on_target: Option<EntityId>,
    pub(crate) lock_on_pos: Option<(f32, f32)>,
    // Grace period after state transition to prevent accidental interactions
    pub(crate) state_timer: f32,
    // Bonfire world position
    pub(crate) bonfire_x: f32,
    pub(crate) bonfire_y: f32,
    // Screen dimensions
    pub(crate) screen_w: f32,
    pub(crate) screen_h: f32,
    // Bloodstain (soul retrieval)
    pub(crate) bloodstain_x: f32,
    pub(crate) bloodstain_y: f32,
    pub(crate) bloodstain_souls: u32,
    pub(crate) has_bloodstain: bool,
    // Soul orbs (floating particles from enemy kills)
    pub(crate) soul_orbs: Vec<SoulOrb>,
    // World item pickups
    pub(crate) items: Vec<WorldItem>,
    // Enemy projectiles (arrows)
    pub(crate) projectiles: Vec<Projectile>,
    // Death animation timer (fades in over 2s)
    pub(crate) death_anim_timer: f32,
    // Boss intro text timer (fades out over 3s)
    pub(crate) boss_intro_timer: f32,
    // Heal particle effect timer
    pub(crate) heal_effect_timer: f32,
    // Block spark effects (visual feedback for knight blocking)
    pub(crate) block_sparks: Vec<BlockSpark>,
    // Dust particles from rolls and impacts
    pub(crate) dust_particles: Vec<DustParticle>,
    // Screen flash (parry, critical hit)
    pub(crate) screen_flash: Option<ScreenFlash>,
    // Stagger burst effects on enemies
    pub(crate) stagger_bursts: Vec<BlockSpark>,
    // Parry riposte window timer
    pub(crate) riposte_timer: f32,
    pub(crate) riposte_target_id: EntityId,
    // Floating damage numbers
    pub(crate) damage_numbers: Vec<DamageNumber>,
    // Enemy death dissolve particles
    pub(crate) death_particles: Vec<DeathParticle>,
    // Level-up flash timer
    pub(crate) level_up_flash: f32,
    pub(crate) pickup_notification: Option<(String, f32)>, // (text, timer)
    // Hitstop (freeze frames on heavy hit)
    pub(crate) hitstop_timer: f32,
    // Slow motion on boss death
    pub(crate) slow_motion_timer: f32,
    // Input buffer for queued actions
    pub(crate) input_buffer: BufferedAction,
    pub(crate) input_buffer_timer: f32,
    // Game statistics
    pub(crate) enemies_killed: u32,
    pub(crate) damage_dealt: u32,
    pub(crate) damage_taken: u32,
    pub(crate) death_count: u32,
    pub(crate) play_time: f32,
    // Treasure chests
    pub(crate) chests: Vec<TreasureChest>,
    // NPCs
    pub(crate) npcs: Vec<Npc>,
    // Current area
    pub(crate) area: AreaId,
    // Fog gates (area transitions and boss doors)
    pub(crate) fog_gates: Vec<FogGate>,
    // Bosses defeated per area
    pub(crate) bosses_defeated: Vec<String>,
    // New Game+ cycle (0 = first playthrough, 1 = NG+, etc.)
    pub(crate) ng_plus: u32,
    // Inventory
    pub(crate) inventory: Vec<InventoryItem>,
    pub(crate) show_inventory: bool,
    // Stored areas (for seamless transitions — Cemetery ↔ Firelink)
    pub(crate) stored_areas: std::collections::HashMap<AreaId, StoredArea>,
    // Gundyr door state (opened after defeating boss)
    pub(crate) gundyr_door_open: bool,
    // Vordt defeated — demon transport pending
    pub(crate) vordt_transport_done: bool,
}

pub(crate) struct WorldItem {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) kind: ItemKind,
    pub(crate) collected: bool,
}

#[derive(Clone)]
pub(crate) enum ItemKind {
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
pub(crate) enum ArmorSlot {
    Head,
    Chest,
    Legs,
    Hands,
}

#[derive(Clone, Debug)]
pub(crate) struct InventoryItem {
    pub(crate) name: String,
    pub(crate) kind: InventoryItemKind,
}

#[derive(Clone, Debug)]
#[allow(dead_code)]
pub(crate) enum InventoryItemKind {
    Weapon(crate::combat::weapon::WeaponType),
    Armor(ArmorSlot, String),
    Ring(String),
    Consumable(String),
}

pub(crate) struct SoulOrb {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) vy: f32,
    pub(crate) timer: f32,
    pub(crate) max_time: f32,
}

pub(crate) struct Projectile {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) vx: f32,
    pub(crate) vy: f32,
    pub(crate) damage: i32,
    pub(crate) timer: f32,
}

pub(crate) struct BlockSpark {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) timer: f32,
}

pub(crate) struct DustParticle {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) vx: f32,
    pub(crate) vy: f32,
    pub(crate) timer: f32,
}

pub(crate) struct ScreenFlash {
    pub(crate) timer: f32,
    pub(crate) max_timer: f32,
    pub(crate) color: [f32; 4],
}

pub(crate) struct DamageNumber {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) vy: f32,
    pub(crate) value: i32,
    pub(crate) timer: f32,
    pub(crate) is_player_damage: bool,
}

pub(crate) struct DeathParticle {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) vx: f32,
    pub(crate) vy: f32,
    pub(crate) timer: f32,
    pub(crate) size: f32,
}

#[derive(Clone, Copy, PartialEq)]
pub(crate) enum BufferedAction {
    Attack,
    HeavyAttack,
    Roll,
    None,
}

pub(crate) struct TreasureChest {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) opened: bool,
    pub(crate) loot: ItemKind,
    pub(crate) is_mimic: bool,
    pub(crate) mimic_revealed: bool,
}

pub(crate) struct Npc {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) name: String,
    pub(crate) color: [f32; 4],
    pub(crate) dialogue: Vec<String>,
    pub(crate) dialogue_index: usize,
    pub(crate) talking: bool,
    pub(crate) kind: NpcKind,
}

#[derive(Clone, Copy, PartialEq)]
#[allow(dead_code)]
pub(crate) enum NpcKind {
    LevelUp,      // Emerald Herald — spend souls to level up
    Merchant,     // Buy items with souls
    Blacksmith,   // Upgrade weapons
    Dialogue,     // Story NPC — no shop
}

pub(crate) struct FogGate {
    pub(crate) x: f32,
    pub(crate) y: f32,
    pub(crate) w: f32,
    pub(crate) h: f32,
    pub(crate) destination: AreaId,
    pub(crate) dest_x: f32,
    pub(crate) dest_y: f32,
    pub(crate) active: bool, // deactivated after boss is dead
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
    let texture = textures::create_test_texture(gl);
    let tileset = Tileset::test_tileset(80, 16);
    let chunk = Chunk::test_chunk((0, 0));
    let collision = CollisionGrid::from_chunk(&chunk, &tileset);
    let nav_grid = NavGrid::from_collision_grid(&collision, CHUNK_SIZE, 2);
    let tileset_texture = textures::create_tileset_texture(gl);

    let light_renderer = LightRenderer::new(gl).expect("Failed to create light renderer");
    let post_processor = PostProcessor::new(gl).expect("Failed to create post-processor");
    let ui_renderer = UiRenderer::new(gl).expect("Failed to create UI renderer");

    // Create off-screen FBO for post-processing
    let (scene_fbo, scene_texture) = textures::create_scene_fbo(gl, screen_w, screen_h);

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

    let player_tex = textures::create_player_texture(&gl);
    let enemy_tex = textures::create_enemy_texture(&gl);
    let boss_tex = textures::create_boss_texture(&gl);
    let white_tex = textures::create_white_texture(&gl);
    let bonfire_tex = textures::create_bonfire_texture(&gl);

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

/// Called from JavaScript on mouse move. `sx`/`sy` are screen pixel coords.
#[wasm_bindgen]
pub fn js_mouse_move(sx: f32, sy: f32) {
    unsafe {
        let game_ptr = &raw mut GAME;
        if let Some(g) = &mut *game_ptr {
            g.input.set_mouse(sx, sy);
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
        "f" | "F" => 70,
        "g" | "G" => 71,
        "r" | "R" => 82,
        "s" | "S" => 83,
        "q" | "Q" => 81,
        "w" | "W" => 87,
        "mouse_left" => 128,
        "mouse_right" => 129,
        "wheel_up" => 130,
        "wheel_down" => 131,
        _ => 255,
    }
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

    crate::bridge::renderer::render(game);

    // Clear press flags AFTER game logic has consumed them
    game.input.begin_frame();
}

fn fixed_update(game: &mut Game, dt: f32) {
    match game.state {
        GameState::TitleScreen => crate::bridge::menus::update_title_screen(game),
        GameState::Playing => update_playing(game, dt),
        GameState::DeathScreen => crate::bridge::menus::update_death(game),
        GameState::BonfireMenu => crate::bridge::menus::update_bonfire_menu(game),
        GameState::LevelUpMenu => crate::bridge::menus::update_level_up_menu(game),
        GameState::TravelMenu => crate::bridge::menus::update_travel_menu(game),
        GameState::Victory => crate::bridge::menus::update_victory(game),
        _ => {}
    }
}


pub(crate) fn rebuild_collision(game: &mut Game) {
    game.collision = CollisionGrid::from_chunk(&game.chunk, &game.tileset);
    game.nav_grid = NavGrid::from_collision_grid(&game.collision, CHUNK_SIZE, 2);
}

fn area_level_path(area: AreaId) -> &'static str {
    match area {
        AreaId::CemeteryOfAsh => "../maps/ds2d/CemeteryOfAsh.ldtkl",
        AreaId::FirelinkShrine => "../maps/ds2d/FirelinkShrine.ldtkl",
        AreaId::LothricWall => "../maps/ds2d/LothricWall.ldtkl",
        AreaId::UndeadSettlement => "../maps/ds2d/UndeadSettlement.ldtkl",
        AreaId::CathedralDeep => "../maps/ds2d/CathedralDeep.ldtkl",
        AreaId::Irithyll => "../maps/ds2d/Irithyll.ldtkl",
    }
}

thread_local! {
    static MAP_CACHE: std::cell::RefCell<std::collections::HashMap<String, String>> =
        std::cell::RefCell::new(std::collections::HashMap::new());
}

fn cached_level_json(area: AreaId) -> String {
    let path = area_level_path(area);
    MAP_CACHE.with(|cache| {
        cache.borrow().get(path).cloned()
    }).unwrap_or_else(|| panic!("Map not preloaded: {}", path))
}

#[wasm_bindgen]
pub fn js_register_map(path: &str, json: &str) {
    MAP_CACHE.with(|cache| {
        cache.borrow_mut().insert(path.to_string(), json.to_string());
    });
}

pub(crate) fn area_from_str(s: &str) -> AreaId {
    match s {
        "CemeteryOfAsh" => AreaId::CemeteryOfAsh,
        "FirelinkShrine" | "Majula" => AreaId::FirelinkShrine,
        "LothricWall" => AreaId::LothricWall,
        "UndeadSettlement" | "ForestOfGiants" => AreaId::UndeadSettlement,
        "CathedralDeep" => AreaId::CathedralDeep,
        "Irithyll" | "LostBastille" => AreaId::Irithyll,
        _ => AreaId::FirelinkShrine,
    }
}

pub(crate) fn fill_tiles(chunk: &mut Chunk, tile: TileId, x1: usize, y1: usize, x2: usize, y2: usize) {
    debug_assert!(x1 <= x2 && y1 <= y2, "fill_tiles: inverted bounds ({x1},{y1})-({x2},{y2})");
    let max = CHUNK_SIZE - 1;
    for y in y1.min(max)..=y2.min(max) {
        for x in x1.min(max)..=x2.min(max) {
            chunk.tiles[y][x] = tile;
        }
    }
}

fn apply_level_patches(
    game: &mut Game,
    tile_patches: &[crate::world::map_loader::TilePatch],
) {
    let mut changed_tiles = false;
    for patch in tile_patches {
        let enabled = match patch.condition.as_str() {
            "always" | "" => true,
            "gundyr_door_open" => game.gundyr_door_open
                || game.bosses_defeated.iter().any(|b| b == "IudexGundyr"),
            _ => false,
        };
        if enabled {
            fill_tiles(&mut game.chunk, patch.tile, patch.x1, patch.y1, patch.x2, patch.y2);
            changed_tiles = true;
        }
    }
    if changed_tiles {
        rebuild_collision(game);
    }
}
fn cycle_lock_on_target(game: &mut Game) {
    let current = match game.lock_on_target {
        Some(id) => id,
        None => return,
    };
    let (px, py) = game.player.position();
    // Collect all valid targets with their positions
    let mut targets: Vec<(EntityId, f32, f32)> = game.enemies.iter()
        .filter(|e| !e.is_dead())
        .map(|e| (e.id(), e.position().0, e.position().1))
        .collect();
    if let Some(boss) = game.boss.as_ref() {
        if !boss.is_dead() && boss.boss_activated {
            targets.push((boss.id(), boss.position().0, boss.position().1));
        }
    }
    if targets.len() < 2 { return; }
    // Sort by distance from player
    targets.sort_by(|a, b| {
        let da = (px - a.1).powi(2) + (py - a.2).powi(2);
        let db = (px - b.1).powi(2) + (py - b.2).powi(2);
        da.partial_cmp(&db).unwrap_or(std::cmp::Ordering::Equal)
    });
    // Find current target index and advance to next
    if let Some(idx) = targets.iter().position(|t| t.0 == current) {
        let next = (idx + 1) % targets.len();
        game.lock_on_target = Some(targets[next].0);
    }
}


fn tick_effects(game: &mut Game, dt: f32) {
    game.state_timer += dt;
    game.play_time += dt;

    if game.boss_intro_timer > 0.0 { game.boss_intro_timer -= dt; }
    if game.heal_effect_timer > 0.0 { game.heal_effect_timer -= dt; }

    for spark in &mut game.block_sparks { spark.timer -= dt; }
    game.block_sparks.retain(|s| s.timer > 0.0);

    for burst in &mut game.stagger_bursts { burst.timer -= dt; }
    game.stagger_bursts.retain(|s| s.timer > 0.0);

    for dust in &mut game.dust_particles {
        dust.x += dust.vx * dt;
        dust.y += dust.vy * dt;
        dust.timer -= dt;
    }
    game.dust_particles.retain(|d| d.timer > 0.0);

    if let Some(ref mut flash) = game.screen_flash {
        flash.timer -= dt;
        if flash.timer <= 0.0 { game.screen_flash = None; }
    }

    if game.riposte_timer > 0.0 { game.riposte_timer -= dt; }

    for dn in &mut game.damage_numbers {
        dn.y += dn.vy * dt;
        dn.vy += 30.0 * dt;
        dn.timer -= dt;
    }
    game.damage_numbers.retain(|d| d.timer > 0.0);

    for p in &mut game.death_particles {
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        p.vy += 60.0 * dt;
        p.timer -= dt;
    }
    game.death_particles.retain(|p| p.timer > 0.0);

    if game.level_up_flash > 0.0 { game.level_up_flash -= dt; }
    if let Some((_, ref mut t)) = game.pickup_notification {
        *t -= dt;
        if *t <= 0.0 { game.pickup_notification = None; }
    }

    if game.input_buffer_timer > 0.0 {
        game.input_buffer_timer -= dt;
        if game.input_buffer_timer <= 0.0 {
            game.input_buffer = BufferedAction::None;
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

    // Resolve raw input into game actions
    let left_weapon = &game.player.equipment.left_hand.active();
    let has_shield = left_weapon.weapon_type == crate::combat::weapon::WeaponType::Shield;
    let act = game.input.resolve(has_shield);
    let mv = (act.move_x, act.move_y);
    let attack = act.right_light;
    let heavy_attack = act.right_heavy;
    let left_light = act.left_light;
    let left_heavy = act.left_heavy;
    let block_held = act.block_held;
    let parry = left_heavy;
    let roll = act.roll;
    let interact = act.interact;
    let use_item = act.use_item;
    let lock_on_toggle = act.lock_on;

    // Two-hand weapon toggle
    if act.two_hand {
        game.pickup_notification = Some(("双持切换".into(), 1.0));
    }

    // Gesture
    if act.gesture {
        game.pickup_notification = Some(("表情动作".into(), 1.5));
        game.audio.play_sfx("emote", 0.05, 0.0);
    }

    // Cycle items with arrow keys
    if act.cycle_prev || act.cycle_next {
        game.player.swap_weapon();
    }

    // Close NPC dialogue on ESC (before inventory toggle)
    let talking_npc = game.npcs.iter().any(|n| n.talking);
    if talking_npc && act.menu {
        for npc in &mut game.npcs {
            npc.talking = false;
            npc.dialogue_index = 0;
        }
    } else if act.menu {
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

    // --- World interactions (fog gates, items, chests, NPCs) ---
    if crate::bridge::interactions::tick_interactions(game, interact) {
        return;
    }

    tick_effects(game, dt);

    // Use item (R key): estus first, then consumables
    if use_item {
        if game.player.hp < game.player.max_hp {
            let heal = game.bonfire.use_estus();
            if heal > 0 {
                game.player.hp = (game.player.hp + heal).min(game.player.max_hp);
                game.audio.play_sfx("estus", 0.08, 0.0);
                game.heal_effect_timer = 0.8;
            }
        } else {
            let moss_idx = game.inventory.iter().position(|i| matches!(&i.kind, InventoryItemKind::Consumable(n) if n == "PurpleMoss"));
            if let Some(idx) = moss_idx {
                game.player.poison_timer = 0.0;
                game.player.poison_tick = 0.0;
                game.inventory.remove(idx);
                game.audio.play_sfx("heal", 0.06, 0.0);
            } else {
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

    // Lock-on target cycling with mouse wheel
    if game.lock_on_target.is_some() {
        if game.input.consume_pressed(KeyCode::WheelUp) || game.input.consume_pressed(KeyCode::WheelDown) {
            cycle_lock_on_target(game);
        }
    }

    // Camera: offset toward mouse position
    {
        let cam_offset_x = (game.input.mouse_x - game.screen_w * 0.5) * 0.15;
        let cam_offset_y = (game.input.mouse_y - game.screen_h * 0.5) * 0.15;
        let target_x = game.player.transform.x + cam_offset_x;
        let target_y = game.player.transform.y + cam_offset_y;
        game.camera.x += (target_x - game.camera.x) * 0.1;
        game.camera.y += (target_y - game.camera.y) * 0.1;
    }

    // Player input
    {
        // Buffer actions during stagger/attack/roll
        if attack || left_light || heavy_attack || roll {
            let can_act = matches!(game.player.state, EntityState::Idle | EntityState::Moving);
            if !can_act {
                if attack || left_light { game.input_buffer = BufferedAction::Attack; }
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
                let do_attack = attack || left_light || (buffer_valid && buffered == BufferedAction::Attack);
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

    // --- Combat resolution ---
    crate::bridge::combat::tick_combat(game);

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

pub(crate) fn load_area(game: &mut Game, area: AreaId) {
    game.area = area;
    game.state = GameState::Playing;
    game.time.accumulator = 0.0;
    game.state_timer = 0.0;
    game.lock_on_target = None;

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

    {
        use crate::world::map_loader::{self, ArmorSlot as MArmorSlot, EnemySpawnKind, ItemSpawnKind, NpcSpawnKind};

        fn convert_spawn_kind(kind: ItemSpawnKind) -> ItemKind {
            match kind {
                ItemSpawnKind::SoulOrb(v) => ItemKind::SoulOrb(v),
                ItemSpawnKind::EstusShard => ItemKind::EstusShard,
                ItemSpawnKind::HomewardBone => ItemKind::HomewardBone,
                ItemSpawnKind::PurpleMoss => ItemKind::PurpleMoss,
                ItemSpawnKind::WeaponDrop(wt) => ItemKind::WeaponDrop(wt),
                ItemSpawnKind::ArmorDrop(slot, name) => {
                    let slot = match slot {
                        MArmorSlot::Head => ArmorSlot::Head,
                        MArmorSlot::Chest => ArmorSlot::Chest,
                        MArmorSlot::Legs => ArmorSlot::Legs,
                        MArmorSlot::Hands => ArmorSlot::Hands,
                    };
                    ItemKind::ArmorDrop(slot, name)
                }
                ItemSpawnKind::RingDrop(name) => ItemKind::RingDrop(name),
            }
        }

        let json = cached_level_json(area);
        let parsed = map_loader::ParsedLevel::from_ldtkl(&json).expect("Failed to load map");
        let map_loader::ParsedLevel {
            chunk,
            player_spawn,
            heal_player,
            boss_spawn,
            bonfire,
            enemies,
            items,
            chests,
            npcs,
            lights,
            fog_gates,
            tile_patches,
        } = parsed;

        game.chunk = chunk;
        apply_level_patches(game, &tile_patches);
        game.collision = CollisionGrid::from_chunk(&game.chunk, &game.tileset);
        game.nav_grid = NavGrid::from_collision_grid(&game.collision, CHUNK_SIZE, 2);

        game.player.transform.x = player_spawn.0;
        game.player.transform.y = player_spawn.1;
        if heal_player {
            game.player.hp = game.player.max_hp;
        }

        game.bonfire_x = bonfire.map(|(x, _)| x).unwrap_or(-10000.0);
        game.bonfire_y = bonfire.map(|(_, y)| y).unwrap_or(-10000.0);

        game.enemies = enemies.into_iter().enumerate().map(|(i, s)| {
            let id = (i as u64) + 2;
            match s.kind {
                EnemySpawnKind::HollowSoldier => Enemy::new_hollow_soldier(id, s.x, s.y),
                EnemySpawnKind::Archer => Enemy::new_archer(id, s.x, s.y),
                EnemySpawnKind::Knight => Enemy::new_knight(id, s.x, s.y),
                EnemySpawnKind::MiniBoss => Enemy::new_mini_boss(id, s.x, s.y),
                EnemySpawnKind::Assassin => Enemy::new_assassin(id, s.x, s.y),
                EnemySpawnKind::DarkMage => Enemy::new_dark_mage(id, s.x, s.y),
                EnemySpawnKind::CrystalLizard => Enemy::new_crystal_lizard(id, s.x, s.y),
            }
        }).collect();

        game.items = items.into_iter().map(|s| {
            WorldItem { x: s.x, y: s.y, collected: false, kind: convert_spawn_kind(s.kind) }
        }).collect();

        game.chests = chests.into_iter().map(|s| {
            TreasureChest { x: s.x, y: s.y, opened: false, loot: convert_spawn_kind(s.loot), is_mimic: s.is_mimic, mimic_revealed: false }
        }).collect();

        game.npcs = npcs.into_iter().map(|s| {
            let kind = match s.kind {
                NpcSpawnKind::LevelUp => NpcKind::LevelUp,
                NpcSpawnKind::Merchant => NpcKind::Merchant,
                NpcSpawnKind::Blacksmith => NpcKind::Blacksmith,
                NpcSpawnKind::Dialogue => NpcKind::Dialogue,
            };
            Npc { x: s.x, y: s.y, name: s.name, color: s.color, dialogue: s.dialogue, dialogue_index: 0, talking: false, kind }
        }).collect();

        game.lights = lights.into_iter().map(|l| {
            Light { x: l.x, y: l.y, radius: l.radius, color: l.color, intensity: l.intensity }
        }).collect();

        game.fog_gates = fog_gates.into_iter().map(|fg| {
            let dest = area_from_str(&fg.dest_area);
            let active = if dest == area {
                if let Some(boss_type) = area_boss(area) {
                    !game.bosses_defeated.iter().any(|b| b == boss_defeat_key(boss_type))
                } else {
                    true
                }
            } else if area == AreaId::CemeteryOfAsh && dest == AreaId::FirelinkShrine {
                game.gundyr_door_open || game.bosses_defeated.iter().any(|b| b == "IudexGundyr")
            } else if area == AreaId::CathedralDeep && dest == AreaId::Irithyll {
                !game.bosses_defeated.iter().any(|b| b == "PontiffSulyvahn")
            } else {
                true
            };
            FogGate { x: fg.x, y: fg.y, w: fg.w, h: fg.h, destination: dest, dest_x: fg.dest_x, dest_y: fg.dest_y, active }
        }).collect();

        game.boss = None;
        game.boss_active = false;
        game.boss_defeated = false;
        if let Some(boss_type) = area_boss(area) {
            let already_defeated = game.bosses_defeated.iter().any(|b| b == boss_defeat_key(boss_type));
            if !already_defeated {
                if let Some((bx, by)) = boss_spawn {
                    let boss = match boss_type {
                        BossType::IudexGundyr => crate::entity::boss::Boss::new_iudex_gundyr(100, bx, by),
                        BossType::Vordt => crate::entity::boss::Boss::new_vordt(100, bx, by),
                        BossType::DemonKnight => crate::entity::boss::Boss::new_test_boss(100, bx, by),
                        BossType::Dragonrider => crate::entity::boss::Boss::new_dragonrider(100, bx, by),
                        BossType::RuinSentinel => crate::entity::boss::Boss::new_ruin_sentinel(100, bx, by),
                    };
                    game.boss = Some(boss);
                }
            }
            if already_defeated {
                game.boss_defeated = true;
            }
        }
    }

    // NG+ difficulty scaling
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

