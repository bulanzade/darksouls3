use wasm_bindgen::prelude::*;

use crate::save::save_data::SaveData;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = localStorage)]
    fn setItem(key: &str, value: &str);

    #[wasm_bindgen(js_namespace = localStorage)]
    fn getItem(key: &str) -> Option<String>;
}

/// Save game data to a named slot (synchronous, persists via localStorage).
pub fn save_game(slot: &str, data: &SaveData) -> Result<(), String> {
    let json = data.serialize().map_err(|e| e.to_string())?;
    let key = format!("ds2d_save_{}", slot);
    setItem(&key, &json);
    Ok(())
}

/// Load game data from a named slot (synchronous, reads from localStorage).
pub fn load_game(slot: &str) -> Result<Option<SaveData>, String> {
    let key = format!("ds2d_save_{}", slot);
    match getItem(&key) {
        Some(json) => {
            let save = SaveData::deserialize(&json).map_err(|e| e.to_string())?;
            Ok(Some(save))
        }
        None => Ok(None),
    }
}
