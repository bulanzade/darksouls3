#[derive(Clone, Debug)]
pub struct StaminaPool {
    pub current: f32,
    pub maximum: f32,
    pub regen_rate: f32,
    pub regen_delay: f32,
    pub regen_timer: f32,
}

impl StaminaPool {
    pub fn new(maximum: f32) -> Self {
        Self {
            current: maximum,
            maximum,
            regen_rate: 40.0,
            regen_delay: 0.5,
            regen_timer: 0.0,
        }
    }

    pub fn consume(&mut self, amount: f32) -> bool {
        if self.current >= amount {
            self.current -= amount;
            self.regen_timer = self.regen_delay;
            true
        } else {
            false
        }
    }

    pub fn update(&mut self, dt: f32, is_acting: bool) {
        if is_acting {
            self.regen_timer = self.regen_delay;
        }

        if self.regen_timer > 0.0 {
            self.regen_timer -= dt;
        } else {
            self.current = (self.current + self.regen_rate * dt).min(self.maximum);
        }
    }

    pub fn ratio(&self) -> f32 {
        self.current / self.maximum
    }
}
