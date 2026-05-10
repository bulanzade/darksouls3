use crate::combat::weapon::WeaponType;
use crate::render::light_renderer::Light;
use crate::world::chunk::Chunk;
use crate::world::tileset::TileId;

#[derive(Debug)]
pub struct EnemySpawn {
    pub x: f32,
    pub y: f32,
    pub kind: EnemySpawnKind,
}

#[derive(Debug)]
pub enum EnemySpawnKind {
    HollowSoldier,
    Archer,
    Knight,
    MiniBoss,
    Assassin,
    DarkMage,
    CrystalLizard,
    // DS3-specific
    SilverKnight,
    BlackKnight,
    DeepAccursed,
    Evangelist,
    Thrall,
    LothricKnight,
    WingedKnight,
    Ghru,
    Darkwraith,
    Skeleton,
    Jailer,
    SerpentMan,
    Deacon,
    FireDemon,
    StarvedHound,
    PusOfMan,
    CathedralKnight,
    ManGrub,
    Gargoyle,
    Dog,
    Basilisk,
    DemonStatue,
    InfestedCorpse,
    Wretch,
    PeasantHollow,
    Mimic,
    GiantSlave,
    HollowAssassin,
    CathedralGraveWarden,
    Rat,
}

#[derive(Debug)]
pub struct ItemSpawn {
    pub x: f32,
    pub y: f32,
    pub kind: ItemSpawnKind,
}

#[derive(Debug)]
pub enum ItemSpawnKind {
    SoulOrb(u32),
    EstusShard,
    HomewardBone,
    PurpleMoss,
    WeaponDrop(WeaponType),
    ArmorDrop(ArmorSlot, String),
    RingDrop(String),
    TitaniteShard,
    Firebomb,
    Ember,
    UndeadBoneShard,
    Consumable(String),
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ArmorSlot {
    Head,
    Chest,
    Legs,
    Hands,
}

#[derive(Debug)]
pub struct ChestSpawn {
    pub x: f32,
    pub y: f32,
    pub loot: ItemSpawnKind,
    pub is_mimic: bool,
}

#[derive(Debug)]
pub struct NpcSpawn {
    pub x: f32,
    pub y: f32,
    pub name: String,
    pub color: [f32; 4],
    pub dialogue: Vec<String>,
    pub kind: NpcSpawnKind,
    pub appear_condition: String,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum NpcSpawnKind {
    LevelUp,
    Merchant,
    Blacksmith,
    Dialogue,
}

#[derive(Debug)]
pub struct FogGateSpawn {
    pub x: f32,
    pub y: f32,
    pub w: f32,
    pub h: f32,
    pub dest_area: String,
    pub dest_x: f32,
    pub dest_y: f32,
}

#[derive(Debug)]
pub struct TilePatch {
    pub tile: TileId,
    pub x1: usize,
    pub y1: usize,
    pub x2: usize,
    pub y2: usize,
    pub condition: String,
}

#[derive(Debug)]
pub struct ParsedLevel {
    pub chunk: Chunk,
    pub player_spawn: (f32, f32),
    pub heal_player: bool,
    pub boss_spawn: Option<(f32, f32)>,
    pub bonfire: Option<(f32, f32)>,
    pub enemies: Vec<EnemySpawn>,
    pub items: Vec<ItemSpawn>,
    pub chests: Vec<ChestSpawn>,
    pub npcs: Vec<NpcSpawn>,
    pub lights: Vec<Light>,
    pub fog_gates: Vec<FogGateSpawn>,
    pub tile_patches: Vec<TilePatch>,
}

impl ParsedLevel {
    pub fn from_ldtkl(json: &str) -> Result<Self, String> {
        let level: ldtk2::Level = serde_json::from_str(json)
            .map_err(|e| format!("LDtk parse error: {}", e))?;

        let layers = level.layer_instances.ok_or("No layer instances in level")?;

        // Extract terrain
        let terrain = layers.iter().find(|l| l.identifier == "Terrain")
            .ok_or("No 'Terrain' layer found")?;
        let width = terrain.c_wid as usize;
        let height = terrain.c_hei as usize;
        if width == 0 || height == 0 {
            return Err(format!("Terrain layer has invalid size {}x{}", width, height));
        }
        let mut chunk = Chunk::with_size((0, 0), width, height);
        for y in 0..height {
            for x in 0..width {
                let idx = y * width + x;
                let val = terrain.int_grid_csv.get(idx).copied().unwrap_or(0);
                chunk.tiles[y][x] = int_to_tile(val);
            }
        }

        // Extract entities
        let entities_layer = layers.iter().find(|l| l.identifier == "Entities")
            .ok_or("No 'Entities' layer found")?;

        let mut player_spawn = (400.0, 400.0);
        let mut heal_player = false;
        let mut boss_spawn = None;
        let mut bonfire = None;
        let mut enemies = Vec::new();
        let mut items = Vec::new();
        let mut chests = Vec::new();
        let mut npcs = Vec::new();
        let mut lights = Vec::new();
        let mut fog_gates = Vec::new();
        let mut tile_patches = Vec::new();

        for entity in &entities_layer.entity_instances {
            let px = entity.px.get(0).copied().unwrap_or(0) as f32;
            let py = entity.px.get(1).copied().unwrap_or(0) as f32;
            let fld = FieldReader::new(&entity.field_instances);

            match entity.identifier.as_str() {
                "PlayerSpawn" => {
                    player_spawn = (px, py);
                    heal_player = fld.bool_val("heal");
                }
                "BossSpawn" => {
                    boss_spawn = Some((px, py));
                }
                "Bonfire" => {
                    bonfire = Some((px, py));
                }
                "Enemy" => {
                    let kind = match fld.str_val("kind").as_str() {
                        "HollowSoldier" => EnemySpawnKind::HollowSoldier,
                        "Archer" => EnemySpawnKind::Archer,
                        "Knight" => EnemySpawnKind::Knight,
                        "MiniBoss" => EnemySpawnKind::MiniBoss,
                        "Assassin" => EnemySpawnKind::Assassin,
                        "DarkMage" => EnemySpawnKind::DarkMage,
                        "CrystalLizard" => EnemySpawnKind::CrystalLizard,
                        "SilverKnight" => EnemySpawnKind::SilverKnight,
                        "BlackKnight" => EnemySpawnKind::BlackKnight,
                        "DeepAccursed" => EnemySpawnKind::DeepAccursed,
                        "Evangelist" => EnemySpawnKind::Evangelist,
                        "Thrall" => EnemySpawnKind::Thrall,
                        "LothricKnight" => EnemySpawnKind::LothricKnight,
                        "WingedKnight" => EnemySpawnKind::WingedKnight,
                        "Ghru" => EnemySpawnKind::Ghru,
                        "Darkwraith" => EnemySpawnKind::Darkwraith,
                        "Skeleton" => EnemySpawnKind::Skeleton,
                        "Jailer" => EnemySpawnKind::Jailer,
                        "SerpentMan" => EnemySpawnKind::SerpentMan,
                        "Deacon" => EnemySpawnKind::Deacon,
                        "FireDemon" => EnemySpawnKind::FireDemon,
                        "StarvedHound" => EnemySpawnKind::StarvedHound,
                        "PusOfMan" => EnemySpawnKind::PusOfMan,
                        "CathedralKnight" => EnemySpawnKind::CathedralKnight,
                        "ManGrub" => EnemySpawnKind::ManGrub,
                        "Gargoyle" => EnemySpawnKind::Gargoyle,
                        "Dog" => EnemySpawnKind::Dog,
                        "Basilisk" => EnemySpawnKind::Basilisk,
                        "DemonStatue" => EnemySpawnKind::DemonStatue,
                        "InfestedCorpse" => EnemySpawnKind::InfestedCorpse,
                        "Wretch" => EnemySpawnKind::Wretch,
                        "PeasantHollow" => EnemySpawnKind::PeasantHollow,
                        "Mimic" => EnemySpawnKind::Mimic,
                        "GiantSlave" => EnemySpawnKind::GiantSlave,
                        "HollowAssassin" => EnemySpawnKind::HollowAssassin,
                        "CathedralGraveWarden" => EnemySpawnKind::CathedralGraveWarden,
                        "Rat" => EnemySpawnKind::Rat,
                        other => return Err(format!("Unknown enemy kind: {}", other)),
                    };
                    enemies.push(EnemySpawn { x: px, y: py, kind });
                }
                "Item" => {
                    let kind = parse_item_kind(&fld)?;
                    items.push(ItemSpawn { x: px, y: py, kind });
                }
                "Chest" => {
                    let loot = parse_item_kind_from(&fld, "loot_kind", "loot_value", "loot_name")?;
                    let is_mimic = fld.bool_val("is_mimic");
                    chests.push(ChestSpawn { x: px, y: py, loot, is_mimic });
                }
                "Npc" => {
                    let kind = match fld.str_val("kind").as_str() {
                        "LevelUp" => NpcSpawnKind::LevelUp,
                        "Merchant" => NpcSpawnKind::Merchant,
                        "Blacksmith" => NpcSpawnKind::Blacksmith,
                        "Dialogue" => NpcSpawnKind::Dialogue,
                        other => return Err(format!("Unknown NPC kind: {}", other)),
                    };
                    let name = fld.str_val("name");
                    let color = fld.color_val("color");
                    let dialogue: Vec<String> = fld.str_val("dialogue")
                        .split('|').map(|s| s.to_string()).collect();
                    let appear_condition = fld.str_val("appear_condition");
                    npcs.push(NpcSpawn { x: px, y: py, name, color, dialogue, kind, appear_condition });
                }
                "Light" => {
                    let radius = fld.f32_val("radius");
                    let intensity = fld.f32_val("intensity");
                    let r = fld.f32_val("r");
                    let g = fld.f32_val("g");
                    let b = fld.f32_val("b");
                    lights.push(Light { x: px, y: py, radius, color: [r, g, b], intensity });
                }
                "FogGate" => {
                    let dest_area = fld.str_val("dest_area");
                    let dest_x = fld.f32_val("dest_x");
                    let dest_y = fld.f32_val("dest_y");
                    let w = fld.f32_val_or("width", entity.width as f32);
                    let h = fld.f32_val_or("height", entity.height as f32);
                    fog_gates.push(FogGateSpawn { x: px, y: py, w, h, dest_area, dest_x, dest_y });
                }
                "TilePatch" => {
                    let tile = parse_tile_kind(&fld.str_val("tile"))?;
                    let x1 = fld.usize_val("x1");
                    let y1 = fld.usize_val("y1");
                    let x2 = fld.usize_val("x2");
                    let y2 = fld.usize_val("y2");
                    let condition = fld.str_val("condition");
                    tile_patches.push(TilePatch { tile, x1, y1, x2, y2, condition });
                }
                other => return Err(format!("Unknown entity type: {}", other)),
            }
        }

        Ok(ParsedLevel {
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
        })
    }
}

fn int_to_tile(val: i64) -> TileId {
    match val {
        1 => TileId::Ground,
        2 => TileId::Wall,
        3 => TileId::WallTop,
        4 => TileId::Poison,
        _ => TileId::Empty,
    }
}

fn parse_tile_kind(s: &str) -> Result<TileId, String> {
    match s {
        "Empty" => Ok(TileId::Empty),
        "Ground" => Ok(TileId::Ground),
        "Wall" => Ok(TileId::Wall),
        "WallTop" => Ok(TileId::WallTop),
        "Poison" => Ok(TileId::Poison),
        other => Err(format!("Unknown tile kind: {}", other)),
    }
}

struct FieldReader<'a> {
    fields: &'a [ldtk2::FieldInstance],
}

impl<'a> FieldReader<'a> {
    fn new(fields: &'a [ldtk2::FieldInstance]) -> Self {
        FieldReader { fields }
    }

    fn find(&self, name: &str) -> Option<&ldtk2::FieldInstance> {
        self.fields.iter().find(|f| f.identifier == name)
    }

    fn str_val(&self, name: &str) -> String {
        self.find(name)
            .and_then(|f| f.value.as_ref())
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string()
    }

    fn f32_val(&self, name: &str) -> f32 {
        self.find(name)
            .and_then(|f| f.value.as_ref())
            .and_then(|v| v.as_f64())
            .unwrap_or(0.0) as f32
    }

    fn f32_val_or(&self, name: &str, default: f32) -> f32 {
        let v = self.find(name)
            .and_then(|f| f.value.as_ref())
            .and_then(|v| v.as_f64());
        match v {
            Some(v) => v as f32,
            None => default,
        }
    }

    fn usize_val(&self, name: &str) -> usize {
        self.find(name)
            .and_then(|f| f.value.as_ref())
            .and_then(|v| v.as_u64())
            .unwrap_or(0) as usize
    }

    fn bool_val(&self, name: &str) -> bool {
        self.find(name)
            .and_then(|f| f.value.as_ref())
            .and_then(|v| v.as_bool())
            .unwrap_or(false)
    }

    fn color_val(&self, name: &str) -> [f32; 4] {
        let s = self.str_val(name);
        parse_hex_color(&s)
    }
}

fn parse_hex_color(s: &str) -> [f32; 4] {
    if s.starts_with('#') && s.len() >= 7 {
        let r = u8::from_str_radix(&s[1..3], 16).unwrap_or(255) as f32 / 255.0;
        let g = u8::from_str_radix(&s[3..5], 16).unwrap_or(255) as f32 / 255.0;
        let b = u8::from_str_radix(&s[5..7], 16).unwrap_or(255) as f32 / 255.0;
        [r, g, b, 1.0]
    } else {
        [1.0, 1.0, 1.0, 1.0]
    }
}

fn parse_item_kind(fld: &FieldReader) -> Result<ItemSpawnKind, String> {
    parse_item_kind_from(fld, "kind", "value", "name")
}

fn parse_item_kind_from(fld: &FieldReader, kind_field: &str, value_field: &str, name_field: &str) -> Result<ItemSpawnKind, String> {
    let kind = fld.str_val(kind_field);
    match kind.as_str() {
        "SoulOrb" => {
            let val = fld.find(value_field)
                .and_then(|f| f.value.as_ref())
                .and_then(|v| v.as_i64())
                .unwrap_or(100) as u32;
            Ok(ItemSpawnKind::SoulOrb(val))
        }
        "EstusShard" => Ok(ItemSpawnKind::EstusShard),
        "HomewardBone" => Ok(ItemSpawnKind::HomewardBone),
        "PurpleMoss" => Ok(ItemSpawnKind::PurpleMoss),
        "WeaponDrop" => {
            let wt = parse_weapon_type(&fld.str_val(name_field));
            Ok(ItemSpawnKind::WeaponDrop(wt))
        }
        "ArmorDrop" => {
            let name = fld.str_val(name_field);
            let slot_str = fld.str_val("slot");
            let slot = match slot_str.as_str() {
                "Head" => ArmorSlot::Head,
                "Chest" => ArmorSlot::Chest,
                "Legs" => ArmorSlot::Legs,
                "Hands" => ArmorSlot::Hands,
                _ => {
                    // Infer from name when slot field is missing
                    if name.contains("Helm") || name.contains("Helmet") || name.contains("Crown") {
                        ArmorSlot::Head
                    } else if name.contains("Gauntlet") || name.contains("Gloves") {
                        ArmorSlot::Hands
                    } else if name.contains("Legging") || name.contains("Boots") || name.contains("Greaves") {
                        ArmorSlot::Legs
                    } else {
                        ArmorSlot::Chest
                    }
                }
            };
            Ok(ItemSpawnKind::ArmorDrop(slot, name))
        }
        "RingDrop" => {
            let name = fld.str_val(name_field);
            Ok(ItemSpawnKind::RingDrop(name))
        }
        "TitaniteShard" => Ok(ItemSpawnKind::TitaniteShard),
        "Firebomb" => Ok(ItemSpawnKind::Firebomb),
        "Ember" => Ok(ItemSpawnKind::Ember),
        "UndeadBoneShard" => Ok(ItemSpawnKind::UndeadBoneShard),
        "Consumable" => {
            let name = fld.str_val(name_field);
            Ok(ItemSpawnKind::Consumable(if name.is_empty() { "Consumable".into() } else { name }))
        }
        // Unknown item kinds are treated as consumables with the kind as name
        other => Err(format!("Unknown item kind: {}", other)),
    }
}

fn parse_weapon_type(s: &str) -> WeaponType {
    match s {
        "Longsword" => WeaponType::Longsword,
        "Spear" => WeaponType::Spear,
        "Dagger" => WeaponType::Dagger,
        "Uchigatana" => WeaponType::Uchigatana,
        "GreatAxe" => WeaponType::GreatAxe,
        "Shield" => WeaponType::Shield,
        _ => WeaponType::Longsword,
    }
}
