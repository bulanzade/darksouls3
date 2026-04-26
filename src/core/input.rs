#[derive(Clone, Copy)]
#[repr(usize)]
pub enum KeyCode {
    Space    = 32,
    Shift    = 16,
    Enter    = 13,
    Escape   = 27,
    Left     = 37,
    Up       = 38,
    Right    = 39,
    Down     = 40,
    A        = 65,
    D        = 68,
    E        = 69,
    I        = 73,
    J        = 74,
    K        = 75,
    L        = 76,
    S        = 83,
    W        = 87,
}

pub struct InputState {
    keys: [bool; 256],
    keys_prev: [bool; 256],
}

impl InputState {
    pub fn new() -> Self {
        Self {
            keys: [false; 256],
            keys_prev: [false; 256],
        }
    }

    /// Call at the start of each fixed-update tick to snapshot previous state.
    pub fn begin_frame(&mut self) {
        self.keys_prev = self.keys;
    }

    pub fn set_key(&mut self, code: usize, pressed: bool) {
        if code < 256 {
            self.keys[code] = pressed;
        }
    }

    /// Rising edge — key was just pressed this frame.
    pub fn pressed(&self, key: KeyCode) -> bool {
        let i = key as usize;
        self.keys[i] && !self.keys_prev[i]
    }

    /// Key is currently held down.
    pub fn held(&self, key: KeyCode) -> bool {
        self.keys[key as usize]
    }

    /// Falling edge — key was just released this frame.
    pub fn released(&self, key: KeyCode) -> bool {
        let i = key as usize;
        !self.keys[i] && self.keys_prev[i]
    }

    /// Returns a normalized (x, y) movement vector from WASD / arrow keys.
    pub fn movement(&self) -> (f32, f32) {
        let mut dx: f32 = 0.0;
        let mut dy: f32 = 0.0;

        if self.held(KeyCode::A) || self.held(KeyCode::Left) {
            dx -= 1.0;
        }
        if self.held(KeyCode::D) || self.held(KeyCode::Right) {
            dx += 1.0;
        }
        if self.held(KeyCode::W) || self.held(KeyCode::Up) {
            dy += 1.0;
        }
        if self.held(KeyCode::S) || self.held(KeyCode::Down) {
            dy -= 1.0;
        }

        // Normalize diagonal movement
        let len = (dx * dx + dy * dy).sqrt();
        if len > 0.0 {
            (dx / len, dy / len)
        } else {
            (0.0, 0.0)
        }
    }
}
