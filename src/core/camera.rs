pub struct Camera2D {
    pub x: f32,
    pub y: f32,
    pub zoom: f32,
    pub viewport_w: f32,
    pub viewport_h: f32,
    shake_amount: f32,
    shake_offset_x: f32,
    shake_offset_y: f32,
}

impl Camera2D {
    pub fn new(viewport_w: f32, viewport_h: f32) -> Self {
        Self {
            x: 0.0,
            y: 0.0,
            zoom: 2.0,
            viewport_w,
            viewport_h,
            shake_amount: 0.0,
            shake_offset_x: 0.0,
            shake_offset_y: 0.0,
        }
    }

    /// Smoothly move camera towards a target position.
    pub fn follow(&mut self, target_x: f32, target_y: f32, speed: f32, dt: f32) {
        let t = 1.0 - (-speed * dt).exp();
        self.x += (target_x - self.x) * t;
        self.y += (target_y - self.y) * t;
    }

    /// Decay screen shake.
    pub fn update(&mut self, dt: f32) {
        self.shake_amount *= (1.0 - 8.0 * dt).max(0.0);
        if self.shake_amount < 0.5 {
            self.shake_amount = 0.0;
        }
        // Simple deterministic shake based on position — no rand dependency.
        let angle = self.x * 0.1 + self.y * 0.13;
        self.shake_offset_x = self.shake_amount * angle.sin();
        self.shake_offset_y = self.shake_amount * angle.cos();
    }

    pub fn add_shake(&mut self, amount: f32) {
        self.shake_amount += amount;
    }

    /// Build an orthographic projection matrix centered on the camera position.
    pub fn projection_matrix(&self) -> [f32; 16] {
        let half_w = self.viewport_w / (2.0 * self.zoom);
        let half_h = self.viewport_h / (2.0 * self.zoom);
        let cx = self.x + self.shake_offset_x;
        let cy = self.y + self.shake_offset_y;
        orthographic(
            cx - half_w,
            cx + half_w,
            cy - half_h,
            cy + half_h,
            -1.0,
            1.0,
        )
    }
}

/// Standalone orthographic projection builder.
pub fn orthographic(left: f32, right: f32, bottom: f32, top: f32, near: f32, far: f32) -> [f32; 16] {
    let tx = -(right + left) / (right - left);
    let ty = -(top + bottom) / (top - bottom);
    let tz = -(far + near) / (far - near);
    [
        2.0 / (right - left), 0.0, 0.0, 0.0,
        0.0, 2.0 / (top - bottom), 0.0, 0.0,
        0.0, 0.0, -2.0 / (far - near), 0.0,
        tx, ty, tz, 1.0,
    ]
}
