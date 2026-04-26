use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SaveData {
    pub version: u32,
    pub timestamp: u64,
    pub stats: crate::rpg::stats::CharacterStats,
    pub soul_level: u32,
    pub souls_held: u32,
    pub current_hp: i32,
    pub equipment: crate::rpg::equipment::Equipment,
    pub inventory: Vec<String>,
    pub bonfires_unlocked: Vec<String>,
    pub last_bonfire: String,
    pub areas_visited: Vec<String>,
    pub bosses_defeated: Vec<String>,
    pub position: (f32, f32),
    pub facing: f32,
    pub area_id: String,
}

impl SaveData {
    pub fn new_game() -> Self {
        Self {
            version: 1,
            timestamp: 0,
            stats: crate::rpg::stats::CharacterStats::default(),
            soul_level: 1,
            souls_held: 0,
            current_hp: 500,
            equipment: crate::rpg::equipment::Equipment::default(),
            inventory: vec!["Longsword".into()],
            bonfires_unlocked: vec!["majula".into()],
            last_bonfire: "majula".into(),
            areas_visited: vec!["majula".into()],
            bosses_defeated: vec![],
            position: (256.0, 256.0),
            facing: 0.0,
            area_id: "majula".into(),
        }
    }

    pub fn serialize(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }

    pub fn deserialize(json: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(json)
    }
}
