use wasm_bindgen::prelude::*;

// JS-side audio engine bridge
#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = window)]
    fn ds2d_audio_init();

    #[wasm_bindgen(js_namespace = window)]
    fn ds2d_play_music(track_id: &str, fade_in_ms: f32);

    #[wasm_bindgen(js_namespace = window)]
    fn ds2d_stop_music(fade_out_ms: f32);

    #[wasm_bindgen(js_namespace = window)]
    fn ds2d_play_sfx(sound_id: &str, volume: f32, pan: f32);

    #[wasm_bindgen(js_namespace = window)]
    fn ds2d_set_listener_position(x: f32, y: f32);
}

pub struct AudioEngine;

impl AudioEngine {
    pub fn init() {
        // Check if JS audio functions exist, call init if so
        // For MVP, these are no-ops if JS side isn't loaded
    }

    pub fn play_music(&self, track_id: &str, fade_in_ms: f32) {
        let _ = (track_id, fade_in_ms);
        // Will call ds2d_play_music when JS side is ready
    }

    pub fn stop_music(&self, fade_out_ms: f32) {
        let _ = fade_out_ms;
    }

    pub fn play_sfx(&self, sound_id: &str, volume: f32, pan: f32) {
        let _ = (sound_id, volume, pan);
    }

    pub fn set_listener_position(&self, x: f32, y: f32) {
        let _ = (x, y);
    }

    /// Calculate spatial audio params from source and listener positions
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
