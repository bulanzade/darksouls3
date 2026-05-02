/// Standard gamepad button indices (Gamepad API layout).
#[derive(Clone, Copy)]
#[repr(usize)]
pub enum GpButton {
    A = 0, B = 1, X = 2, Y = 3,
    LB = 4, RB = 5, LT = 6, RT = 7,
    Back = 8, Start = 9,
    L3 = 10, R3 = 11,
    DUp = 12, DDown = 13, DLeft = 14, DRight = 15,
}

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
    pub cycle_left: bool,
    pub cycle_right: bool,
    pub block_held: bool,
    pub sprint: bool,
    pub cam_offset_x: f32,
    pub cam_offset_y: f32,
}

/// Raw gamepad state, updated each frame by JS polling.
pub(crate) struct GamepadState {
    pub active: bool,
    pub lx: f32,
    pub ly: f32,
    pub rx: f32,
    pub ry: f32,
    /// Current held state of 16 digital buttons
    pub buttons: [bool; 16],
    /// Press queue: JS sends edge-detected "just pressed" events as a bitmask.
    /// Persists for INPUT_QUEUE_FRAMES ticks, same as keyboard.
    press_queue: [u8; 16],
    /// Trigger threshold crossing events from JS (bit 0 = LT, bit 1 = RT)
    trigger_queue: [u8; 2],
}

impl GamepadState {
    pub fn new() -> Self {
        Self {
            active: false,
            lx: 0.0, ly: 0.0, rx: 0.0, ry: 0.0,
            buttons: [false; 16],
            press_queue: [0; 16],
            trigger_queue: [0; 2],
        }
    }

    /// Called from js_gamepad: enqueue button presses from JS edge detection.
    pub fn enqueue_presses(&mut self, mask: u32) {
        for i in 0..16 {
            if mask & (1 << i) != 0 {
                self.press_queue[i] = INPUT_QUEUE_FRAMES;
            }
        }
    }

    /// Enqueue trigger threshold crossings from JS.
    pub fn enqueue_triggers(&mut self, lt: bool, rt: bool) {
        if lt { self.trigger_queue[0] = INPUT_QUEUE_FRAMES; }
        if rt { self.trigger_queue[1] = INPUT_QUEUE_FRAMES; }
    }

    pub fn begin_frame(&mut self) {
        for q in &mut self.press_queue {
            if *q > 0 { *q -= 1; }
        }
        for q in &mut self.trigger_queue {
            if *q > 0 { *q -= 1; }
        }
    }

    /// Read and clear — returns true once per press, then consumes.
    pub fn consume_pressed(&mut self, btn: GpButton) -> bool {
        let idx = btn as usize;
        if self.press_queue[idx] > 0 {
            self.press_queue[idx] = 0;
            true
        } else {
            false
        }
    }

    fn consume_trigger(&mut self, idx: usize) -> bool {
        if self.trigger_queue[idx] > 0 {
            self.trigger_queue[idx] = 0;
            true
        } else {
            false
        }
    }
}

pub struct InputState {
    keys: [bool; 256],
    press_queue: [u8; 256],
    pub mouse_x: f32,
    pub mouse_y: f32,
    pub(crate) gamepad: GamepadState,
}

const INPUT_QUEUE_FRAMES: u8 = 3;
const GAMEPAD_DEADZONE: f32 = 0.15;

impl InputState {
    pub fn new() -> Self {
        Self {
            keys: [false; 256],
            press_queue: [0; 256],
            mouse_x: 480.0,
            mouse_y: 270.0,
            gamepad: GamepadState::new(),
        }
    }

    pub fn begin_frame(&mut self) {
        for q in &mut self.press_queue {
            if *q > 0 { *q -= 1; }
        }
        self.gamepad.begin_frame();
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

    pub fn pressed(&self, key: KeyCode) -> bool {
        self.press_queue[key as usize] > 0
    }

    pub fn consume_pressed(&mut self, key: KeyCode) -> bool {
        let idx = key as usize;
        if self.press_queue[idx] > 0 {
            self.press_queue[idx] = 0;
            true
        } else {
            false
        }
    }

    pub fn held(&self, key: KeyCode) -> bool {
        self.keys[key as usize]
    }

    pub fn confirm_pressed(&mut self) -> bool {
        self.consume_pressed(KeyCode::Enter) || self.gamepad.consume_pressed(GpButton::A)
    }

    pub fn cancel_pressed(&mut self) -> bool {
        self.consume_pressed(KeyCode::Escape) || self.gamepad.consume_pressed(GpButton::B)
    }

    pub fn menu_up(&mut self) -> bool {
        self.pressed(KeyCode::Up) || self.gamepad.consume_pressed(GpButton::DUp)
    }

    pub fn menu_down(&mut self) -> bool {
        self.pressed(KeyCode::Down) || self.gamepad.consume_pressed(GpButton::DDown)
    }

    pub fn movement(&self) -> (f32, f32) {
        let mut dx: f32 = 0.0;
        let mut dy: f32 = 0.0;
        if self.held(KeyCode::A) { dx -= 1.0; }
        if self.held(KeyCode::D) { dx += 1.0; }
        if self.held(KeyCode::W) { dy -= 1.0; }
        if self.held(KeyCode::S) { dy += 1.0; }
        let len = (dx * dx + dy * dy).sqrt();
        if len > 0.0 { (dx / len, dy / len) } else { (0.0, 0.0) }
    }

    pub fn resolve(&mut self, has_shield: bool, screen_w: f32, screen_h: f32) -> GameActions {
        let shift = self.held(KeyCode::Shift);
        let ml = self.consume_pressed(KeyCode::MouseLeft);
        let mr = self.consume_pressed(KeyCode::MouseRight);
        let (kb_mx, kb_my) = self.movement();
        let kb_space = self.consume_pressed(KeyCode::Space);
        let kb_e = self.consume_pressed(KeyCode::E);
        let kb_r = self.consume_pressed(KeyCode::R);
        let kb_q = self.consume_pressed(KeyCode::Q);
        let kb_f = self.consume_pressed(KeyCode::F);
        let kb_g = self.consume_pressed(KeyCode::G);
        let kb_esc = self.consume_pressed(KeyCode::Escape);
        let kb_enter = self.consume_pressed(KeyCode::Enter);
        let kb_up = self.consume_pressed(KeyCode::Up);
        let kb_down = self.consume_pressed(KeyCode::Down);
        let mouse_x = self.mouse_x;
        let mouse_y = self.mouse_y;

        let gp = &mut self.gamepad;

        // Consume all gamepad press events (from JS edge detection + press_queue)
        let gp_a = gp.consume_pressed(GpButton::A);
        let gp_b = gp.consume_pressed(GpButton::B);
        let gp_x = gp.consume_pressed(GpButton::X);
        let gp_y = gp.consume_pressed(GpButton::Y);
        let gp_rb = gp.consume_pressed(GpButton::RB);
        let gp_back = gp.consume_pressed(GpButton::Back);
        let gp_start = gp.consume_pressed(GpButton::Start);
        let gp_r3 = gp.consume_pressed(GpButton::R3);
        let gp_du = gp.consume_pressed(GpButton::DUp);
        let gp_dd = gp.consume_pressed(GpButton::DDown);
        let gp_dl = gp.consume_pressed(GpButton::DLeft);
        let gp_dr = gp.consume_pressed(GpButton::DRight);
        let gp_lt = gp.consume_trigger(0);
        let gp_rt = gp.consume_trigger(1);

        // B: press = roll, hold while moving = sprint
        let gp_b_held = gp.active && gp.buttons[GpButton::B as usize];
        let gp_len = (gp.lx * gp.lx + gp.ly * gp.ly).sqrt();
        let gp_moving = gp.active && gp_len > GAMEPAD_DEADZONE;
        let gp_sprint = gp_b_held && gp_moving;
        let gp_roll = gp_b;

        // Movement: gamepad left stick overrides keyboard if past deadzone
        let (mx, my) = if gp.active && gp_len > GAMEPAD_DEADZONE {
            let factor = ((gp_len - GAMEPAD_DEADZONE) / (1.0 - GAMEPAD_DEADZONE)).min(1.0);
            (gp.lx / gp_len * factor, gp.ly / gp_len * factor)
        } else if kb_mx != 0.0 || kb_my != 0.0 {
            (kb_mx, kb_my)
        } else {
            (0.0, 0.0)
        };

        // Camera: right stick overrides mouse
        let rs_len = (gp.rx * gp.rx + gp.ry * gp.ry).sqrt();
        let (gp_cam_x, gp_cam_y) = if gp.active && rs_len > GAMEPAD_DEADZONE {
            (gp.rx * 200.0, gp.ry * 200.0)
        } else {
            (0.0, 0.0)
        };
        let (cam_ox, cam_oy) = if gp_cam_x != 0.0 || gp_cam_y != 0.0 {
            (gp_cam_x, gp_cam_y)
        } else {
            ((mouse_x - screen_w * 0.5) * 0.3, (mouse_y - screen_h * 0.5) * 0.3)
        };

        // LB held = block
        let gp_block = gp.active && gp.buttons[GpButton::LB as usize];

        GameActions {
            move_x: mx,
            move_y: my,
            right_light: (ml && !shift) || gp_rb,
            right_heavy: (ml && shift) || gp_rt,
            left_light: mr && !shift,
            left_heavy: (mr && shift) || gp_lt,
            roll: kb_space || gp_roll,
            interact: kb_e || gp_a,
            use_item: kb_r || gp_x,
            lock_on: kb_q || gp_r3,
            two_hand: kb_f || gp_y,
            gesture: kb_g,
            menu: kb_esc || gp_back || gp_start,
            confirm: kb_enter || gp_a,
            cycle_prev: kb_up || gp_du,
            cycle_next: kb_down || gp_dd,
            cycle_left: gp_dl,
            cycle_right: gp_dr,
            block_held: (mr && !shift && has_shield) || gp_block,
            sprint: gp_sprint,
            cam_offset_x: cam_ox,
            cam_offset_y: cam_oy,
        }
    }
}
