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
    F        = 70,
    G        = 71,
    R        = 82,
    S        = 83,
    Q        = 81,
    W        = 87,
    MouseLeft  = 128,
    MouseRight = 129,
    WheelUp    = 130,
    WheelDown  = 131,
}

/// High-level game actions, decoupled from physical keys.
/// Game logic reads these instead of raw KeyCode values.
pub struct GameActions {
    pub move_x: f32,
    pub move_y: f32,
    pub right_light: bool,
    pub right_heavy: bool,
    pub left_light: bool,
    pub left_heavy: bool,
    pub roll: bool,
    pub interact: bool,
    pub use_item: bool,
    pub lock_on: bool,
    pub two_hand: bool,
    pub gesture: bool,
    pub menu: bool,
    pub confirm: bool,
    pub cycle_prev: bool,
    pub cycle_next: bool,
    pub block_held: bool,
}

pub struct InputState {
    keys: [bool; 256],
    /// Counts down from INPUT_QUEUE_FRAMES when a key is first pressed.
    /// Allows `pressed()` to return true for multiple frames, preventing
    /// swallowed inputs when the game logic can't act immediately.
    press_queue: [u8; 256],
    /// Mouse screen position.
    pub mouse_x: f32,
    pub mouse_y: f32,
}

/// How many frames a "pressed" event stays alive.
const INPUT_QUEUE_FRAMES: u8 = 3;

impl InputState {
    pub fn new() -> Self {
        Self {
            keys: [false; 256],
            press_queue: [0; 256],
            mouse_x: 480.0,
            mouse_y: 270.0,
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

    pub fn set_mouse(&mut self, x: f32, y: f32) {
        self.mouse_x = x;
        self.mouse_y = y;
    }

    /// Key was pressed recently (within INPUT_QUEUE_FRAMES ticks).
    pub fn pressed(&self, key: KeyCode) -> bool {
        self.press_queue[key as usize] > 0
    }

    /// Read and clear — returns true once per key press, then consumes the event.
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

    /// Returns a normalized (x, y) movement vector from WASD.
    pub fn movement(&self) -> (f32, f32) {
        let mut dx: f32 = 0.0;
        let mut dy: f32 = 0.0;

        if self.held(KeyCode::A) {
            dx -= 1.0;
        }
        if self.held(KeyCode::D) {
            dx += 1.0;
        }
        if self.held(KeyCode::W) {
            dy -= 1.0;
        }
        if self.held(KeyCode::S) {
            dy += 1.0;
        }

        let len = (dx * dx + dy * dy).sqrt();
        if len > 0.0 {
            (dx / len, dy / len)
        } else {
            (0.0, 0.0)
        }
    }

    /// Resolve current raw inputs into high-level game actions.
    /// `has_shield` controls whether left_light triggers block stance.
    pub fn resolve(&mut self, has_shield: bool) -> GameActions {
        let shift = self.held(KeyCode::Shift);
        let ml = self.consume_pressed(KeyCode::MouseLeft);
        let mr = self.consume_pressed(KeyCode::MouseRight);
        let (mx, my) = self.movement();

        GameActions {
            move_x: mx,
            move_y: my,
            right_light: ml && !shift,
            right_heavy: ml && shift,
            left_light: mr && !shift,
            left_heavy: mr && shift,
            roll: self.consume_pressed(KeyCode::Space),
            interact: self.consume_pressed(KeyCode::E),
            use_item: self.consume_pressed(KeyCode::R),
            lock_on: self.consume_pressed(KeyCode::Q),
            two_hand: self.consume_pressed(KeyCode::F),
            gesture: self.consume_pressed(KeyCode::G),
            menu: self.consume_pressed(KeyCode::Escape),
            confirm: self.consume_pressed(KeyCode::Enter),
            cycle_prev: self.consume_pressed(KeyCode::Up),
            cycle_next: self.consume_pressed(KeyCode::Down),
            block_held: mr && !shift && has_shield,
        }
    }
}
