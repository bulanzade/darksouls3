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
    Q        = 81,
    Tab      = 9,
    W        = 87,
    Num1     = 49,
    Num2     = 50,
    MouseLeft  = 128,
    MouseRight = 129,
    WheelUp    = 130,
    WheelDown  = 131,
}

pub struct InputState {
    keys: [bool; 256],
    /// Counts down from INPUT_QUEUE_FRAMES when a key is first pressed.
    /// Allows `pressed()` to return true for multiple frames, preventing
    /// swallowed inputs when the game logic can't act immediately.
    press_queue: [u8; 256],
}

/// How many frames a "pressed" event stays alive.
const INPUT_QUEUE_FRAMES: u8 = 3;

impl InputState {
    pub fn new() -> Self {
        Self {
            keys: [false; 256],
            press_queue: [0; 256],
        }
    }

    /// Decrement press queue timers. Call at the end of each tick.
    pub fn begin_frame(&mut self) {
        for q in &mut self.press_queue {
            if *q > 0 {
                *q -= 1;
            }
        }
    }

    pub fn set_key(&mut self, code: usize, pressed: bool) {
        if code < 256 {
            if pressed && !self.keys[code] {
                self.press_queue[code] = INPUT_QUEUE_FRAMES;
            }
            self.keys[code] = pressed;
        }
    }

    /// Key was pressed recently (within INPUT_QUEUE_FRAMES ticks).
    /// Persists across frames so game logic won't miss fast taps.
    pub fn pressed(&self, key: KeyCode) -> bool {
        self.press_queue[key as usize] > 0
    }

    /// Read and clear — returns true once per key press, then consumes the event.
    /// Use for one-shot actions like estus, interact, menu confirm.
    pub fn consume_pressed(&mut self, key: KeyCode) -> bool {
        let idx = key as usize;
        if self.press_queue[idx] > 0 {
            self.press_queue[idx] = 0;
            true
        } else {
            false
        }
    }

    /// Key is currently held down.
    pub fn held(&self, key: KeyCode) -> bool {
        self.keys[key as usize]
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
            dy -= 1.0;
        }
        if self.held(KeyCode::S) || self.held(KeyCode::Down) {
            dy += 1.0;
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
