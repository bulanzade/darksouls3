//! Save/load system using browser LocalStorage via wasm-bindgen.
//!
//! Provides a self-contained `SaveData` struct with the essential game state
//! and functions to persist/restore it from `localStorage` under the key
//! `"ds2d_save"`.

use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;

use crate::save::bonfire::BonfireState;

const SAVE_KEY: &str = "ds2d_save";

/// Minimal snapshot of game state that gets persisted to localStorage.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SaveData {
    pub player_level: u32,
    pub vigor: u32,
    pub endurance: u32,
    pub strength: u32,
    pub souls: u32,
    pub bonfire: BonfireState,
    pub current_room: String,
    pub player_hp: i32,
    pub player_x: f32,
    pub player_y: f32,
    pub weapon_name: String,
    pub weapon_damage: i32,
    pub alt_weapon_name: Option<String>,
    pub alt_weapon_damage: Option<i32>,
    pub bosses_defeated: Vec<String>,
    pub enemies_killed: u32,
    pub items_collected: Vec<String>,
    pub chests_opened: Vec<String>,
    pub play_time: f32,
    pub death_count: u32,
    pub damage_dealt: u32,
    pub damage_taken: u32,
}

// ---------------------------------------------------------------------------
// wasm-bindgen extern bindings to localStorage
// ---------------------------------------------------------------------------

#[wasm_bindgen(inline_js = r#"
export function ls_setItem(key, value) {
    try { localStorage.setItem(key, value); } catch(e) { console.error("ls_setItem", e); }
}
export function ls_getItem(key) {
    try { return localStorage.getItem(key); } catch(e) { console.error("ls_getItem", e); return null; }
}
export function ls_removeItem(key) {
    try { localStorage.removeItem(key); } catch(e) { console.error("ls_removeItem", e); }
}
"#)]
extern "C" {
    fn ls_setItem(key: &str, value: &str);
    fn ls_getItem(key: &str) -> Option<String>;
    fn ls_removeItem(key: &str);
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/// Serialize `data` to JSON and write it to localStorage.
pub fn save_to_localstorage(data: &SaveData) {
    match serde_json::to_string(data) {
        Ok(json) => ls_setItem(SAVE_KEY, &json),
        Err(e) => log::error!("save_to_localstorage serialize error: {}", e),
    }
}

/// Load and deserialize `SaveData` from localStorage.
/// Returns `None` if no save exists or deserialization fails.
pub fn load_from_localstorage() -> Option<SaveData> {
    let json = ls_getItem(SAVE_KEY)?;
    match serde_json::from_str::<SaveData>(&json) {
        Ok(data) => Some(data),
        Err(e) => {
            log::error!("load_from_localstorage deserialize error: {}", e);
            None
        }
    }
}

/// Check whether a save exists in localStorage.
pub fn has_save() -> bool {
    ls_getItem(SAVE_KEY).is_some()
}

/// Remove the save entry from localStorage.
pub fn delete_save() {
    ls_removeItem(SAVE_KEY);
}

// ---------------------------------------------------------------------------
// Tests (run with `cargo test --target x86_64-unknown-linux-gnu` etc.)
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roundtrip_serialization() {
        let data = SaveData {
            player_level: 12,
            vigor: 8,
            endurance: 6,
            strength: 10,
            souls: 3400,
            bonfire: BonfireState::new(),
            current_room: "firelink".into(),
        };
        let json = serde_json::to_string(&data).unwrap();
        let loaded: SaveData = serde_json::from_str(&json).unwrap();
        assert_eq!(loaded.player_level, 12);
        assert_eq!(loaded.souls, 3400);
        assert_eq!(loaded.current_room, "firelink");
        assert_eq!(loaded.bonfire.estus_charges, 5);
    }
}
