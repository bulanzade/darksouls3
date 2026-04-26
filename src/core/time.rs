pub const FIXED_DT: f64 = 1.0 / 60.0;
const MAX_FRAME_TIME: f64 = 0.1; // 100 ms

pub struct Time {
    accumulator: f64,
    last_timestamp: Option<f64>,
}

impl Time {
    pub fn new() -> Self {
        Self {
            accumulator: 0.0,
            last_timestamp: None,
        }
    }

    pub fn update(&mut self, timestamp_ms: f64) {
        let ts = timestamp_ms / 1000.0; // convert to seconds
        match self.last_timestamp {
            None => {
                // First frame — don't accumulate
                self.last_timestamp = Some(ts);
            }
            Some(prev) => {
                let frame_time = (ts - prev).min(MAX_FRAME_TIME);
                self.last_timestamp = Some(ts);
                self.accumulator += frame_time;
            }
        }
    }

    pub fn should_fixed_update(&mut self) -> bool {
        if self.accumulator >= FIXED_DT {
            self.accumulator -= FIXED_DT;
            true
        } else {
            false
        }
    }
}
