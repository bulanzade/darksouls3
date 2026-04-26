/// A blend layer for mixing multiple animations
pub struct BlendLayer {
    pub animation_name: Option<String>,
    pub time: f32,
    pub weight: f32,             // 0.0-1.0, how much this layer contributes
    pub bone_mask: Vec<usize>,   // Indices of bones this layer affects (empty = all)
    pub speed: f32,
}

impl BlendLayer {
    pub fn full_body(anim_name: &str) -> Self {
        Self {
            animation_name: Some(anim_name.into()),
            time: 0.0,
            weight: 1.0,
            bone_mask: vec![],  // Empty = all bones
            speed: 1.0,
        }
    }

    pub fn with_bone_mask(anim_name: &str, bones: Vec<usize>) -> Self {
        Self {
            animation_name: Some(anim_name.into()),
            time: 0.0,
            weight: 1.0,
            bone_mask: bones,
            speed: 1.0,
        }
    }

    pub fn empty() -> Self {
        Self {
            animation_name: None,
            time: 0.0,
            weight: 0.0,
            bone_mask: vec![],
            speed: 1.0,
        }
    }

    pub fn affects_bone(&self, bone_index: usize) -> bool {
        self.bone_mask.is_empty() || self.bone_mask.contains(&bone_index)
    }
}

/// Manages crossfade blending between animations
pub struct AnimationBlender {
    pub base_layer: BlendLayer,
    pub blend_target: Option<BlendTarget>,
    pub blend_duration: f32,
    pub blend_timer: f32,
    pub is_blending: bool,
}

pub struct BlendTarget {
    pub animation_name: String,
    pub bone_mask: Vec<usize>,
    pub speed: f32,
}

impl AnimationBlender {
    pub fn new(initial_anim: &str) -> Self {
        Self {
            base_layer: BlendLayer::full_body(initial_anim),
            blend_target: None,
            blend_duration: 0.0,
            blend_timer: 0.0,
            is_blending: false,
        }
    }

    /// Start a crossfade to a new animation
    pub fn crossfade(&mut self, target_anim: &str, duration: f32, bone_mask: Vec<usize>) {
        if let Some(ref current) = self.base_layer.animation_name {
            if current == target_anim {
                return; // Already playing this animation
            }
        }

        self.blend_target = Some(BlendTarget {
            animation_name: target_anim.into(),
            bone_mask,
            speed: 1.0,
        });
        self.blend_duration = duration;
        self.blend_timer = 0.0;
        self.is_blending = true;
    }

    /// Quick crossfade presets
    pub fn crossfade_full(&mut self, target: &str, duration: f32) {
        self.crossfade(target, duration, vec![]);
    }

    /// Upper body only blend (for attack-while-walking)
    pub fn crossfade_upper(&mut self, target: &str, duration: f32, upper_bones: Vec<usize>) {
        self.crossfade(target, duration, upper_bones);
    }

    /// Snap to animation (instant, no blend)
    pub fn snap_to(&mut self, target: &str) {
        self.base_layer.animation_name = Some(target.into());
        self.base_layer.time = 0.0;
        self.blend_target = None;
        self.is_blending = false;
    }

    /// Update blend and return current blend weight (0.0-1.0, how much of target)
    pub fn update(&mut self, dt: f32) -> f32 {
        if !self.is_blending {
            self.base_layer.time += dt * self.base_layer.speed;
            return 0.0;
        }

        self.blend_timer += dt;
        self.base_layer.time += dt * self.base_layer.speed;

        let t = if self.blend_duration > 0.0 {
            (self.blend_timer / self.blend_duration).min(1.0)
        } else {
            1.0
        };

        // Blend complete
        if t >= 1.0 {
            if let Some(target) = self.blend_target.take() {
                self.base_layer.animation_name = Some(target.animation_name);
                self.base_layer.time = 0.0;
                self.base_layer.speed = target.speed;
            }
            self.is_blending = false;
            return 1.0;
        }

        t
    }

    /// Get current animation names (base, optional target)
    pub fn current_animations(&self) -> (&Option<String>, Option<&String>) {
        let target_name = self.blend_target.as_ref().map(|t| &t.animation_name);
        (&self.base_layer.animation_name, target_name)
    }

    /// Linear interpolation helper for bone transforms
    pub fn lerp_bone(
        from_x: f32, from_y: f32, from_rot: f32, from_sx: f32, from_sy: f32,
        to_x: f32, to_y: f32, to_rot: f32, to_sx: f32, to_sy: f32,
        t: f32,
    ) -> (f32, f32, f32, f32, f32) {
        let x = from_x + (to_x - from_x) * t;
        let y = from_y + (to_y - from_y) * t;
        let rot = lerp_angle(from_rot, to_rot, t);
        let sx = from_sx + (to_sx - from_sx) * t;
        let sy = from_sy + (to_sy - from_sy) * t;
        (x, y, rot, sx, sy)
    }
}

fn lerp_angle(a: f32, b: f32, t: f32) -> f32 {
    let diff = ((b - a + std::f32::consts::PI) % (2.0 * std::f32::consts::PI)) - std::f32::consts::PI;
    a + diff * t
}
