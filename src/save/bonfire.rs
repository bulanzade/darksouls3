use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BonfireDef {
    pub id: String,
    pub name: String,
    pub area_id: String,
    pub position: (f32, f32),
    pub is_lit: bool,
}

impl BonfireDef {
    pub fn new(id: &str, name: &str, area_id: &str, x: f32, y: f32) -> Self {
        Self {
            id: id.into(),
            name: name.into(),
            area_id: area_id.into(),
            position: (x, y),
            is_lit: false,
        }
    }
}

#[derive(Clone, Debug)]
pub struct BonfireState {
    pub unlocked_bonfires: Vec<String>,
    pub estus_charges: u32,
    pub estus_max: u32,
}

impl BonfireState {
    pub fn new() -> Self {
        Self {
            unlocked_bonfires: vec!["majula".into()],
            estus_charges: 5,
            estus_max: 5,
        }
    }

    pub fn rest(&mut self) {
        self.estus_charges = self.estus_max;
    }

    pub fn unlock(&mut self, bonfire_id: &str) {
        if !self.unlocked_bonfires.contains(&bonfire_id.to_string()) {
            self.unlocked_bonfires.push(bonfire_id.into());
        }
    }

    pub fn use_estus(&mut self) -> i32 {
        if self.estus_charges > 0 {
            self.estus_charges -= 1;
            200 // HP restored
        } else {
            0
        }
    }
}
