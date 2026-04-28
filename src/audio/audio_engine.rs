use wasm_bindgen::prelude::*;

#[wasm_bindgen(inline_js = r#"
export function ds2d_play_sfx_js(sound_id, volume, pan) {
    if (window.ds2d_play_sfx) {
        window.ds2d_play_sfx(sound_id, volume, pan);
    }
}
export function ds2d_combat_music_js(active) {
    if (window.ds2d_combat_music) {
        window.ds2d_combat_music(active);
    }
}
"#)]
extern "C" {
    fn ds2d_play_sfx_js(sound_id: &str, volume: f32, pan: f32);
    fn ds2d_combat_music_js(active: bool);
}

pub struct AudioEngine;

impl AudioEngine {
    pub fn play_sfx(&self, sound_id: &str, volume: f32, pan: f32) {
        ds2d_play_sfx_js(sound_id, volume, pan);
    }

    pub fn set_listener_position(&self, _x: f32, _y: f32) {}

    pub fn set_combat_music(&self, active: bool) {
        ds2d_combat_music_js(active);
    }

    pub fn spatial_params(
        listener_x: f32,
        listener_y: f32,
        source_x: f32,
        source_y: f32,
        attenuation: f32,
    ) -> (f32, f32) {
        let dx = source_x - listener_x;
        let dy = source_y - listener_y;
        let dist = (dx * dx + dy * dy).sqrt();
        let pan = (dx / (dist + 0.001)).clamp(-1.0, 1.0);
        let volume = (1.0 / (1.0 + dist * attenuation)).clamp(0.0, 1.0);
        (volume, pan)
    }
}
