use crate::dragonbones::armature::{Armature, BoneKeyframe, SlotKeyframe};

/// Drives animation playback on an Armature.
pub struct AnimationPlayer {
    pub current_animation: Option<String>,
    pub time: f32,
    pub playing: bool,
    pub loop_count: i32,
    pub speed: f32,
}

impl AnimationPlayer {
    pub fn new() -> Self {
        Self {
            current_animation: None,
            time: 0.0,
            playing: false,
            loop_count: 0,
            speed: 1.0,
        }
    }

    /// Start playing an animation. loop_count: -1 = loop forever, 0 = play once, N = play N times.
    pub fn play(&mut self, name: &str, loop_count: i32) {
        self.current_animation = Some(name.to_string());
        self.time = 0.0;
        self.playing = true;
        self.loop_count = loop_count;
    }

    /// Advance the animation by dt seconds and update the armature's bone transforms.
    pub fn update(&mut self, dt: f32, armature: &mut Armature) {
        let anim_name = match &self.current_animation {
            Some(n) => n.clone(),
            None => return,
        };

        let clip = match armature.animations.get(&anim_name) {
            Some(c) => c.clone(), // Clone to avoid borrowing issues
            None => return,
        };

        if !self.playing {
            return;
        }

        // Advance time
        self.time += dt * self.speed;

        // Handle looping
        let duration = clip.duration;
        if duration > 0.0 && self.time >= duration {
            if self.loop_count == -1 {
                // Loop forever
                self.time %= duration;
            } else if self.loop_count > 0 {
                self.loop_count -= 1;
                self.time %= duration;
            } else {
                // Play once — clamp and stop
                self.time = duration;
                self.playing = false;
            }
        }

        let t = self.time;

        // Reset all bone local transforms to identity
        for bone in &mut armature.bones {
            bone.reset_local();
        }

        // Evaluate bone timelines
        for (bone_name, timeline) in &clip.bone_timelines {
            let bone_idx = match armature.bones.iter().position(|b| b.name == *bone_name) {
                Some(i) => i,
                None => continue,
            };

            if timeline.frames.is_empty() {
                continue;
            }

            let (kf_a, kf_b, local_t) = find_bone_frame_pair(&timeline.frames, t, duration);

            let eased_t = apply_easing(local_t, kf_a.easing);

            let x = lerp(kf_a.x, kf_b.x, eased_t);
            let y = lerp(kf_a.y, kf_b.y, eased_t);
            let rotation = lerp_angle(kf_a.rotation, kf_b.rotation, eased_t);
            // Scale: delta from 1.0, so we lerp the scale values directly
            let scale_x = lerp(kf_a.scale_x, kf_b.scale_x, eased_t);
            let scale_y = lerp(kf_a.scale_y, kf_b.scale_y, eased_t);

            // local_* are deltas from rest pose
            // The keyframe values are absolute local transforms, so delta = keyframe - rest
            let rest = &armature.bones[bone_idx];
            let rest_x = rest.rest_x;
            let rest_y = rest.rest_y;
            let rest_rot = rest.rest_rotation;
            let rest_sx = rest.rest_scale_x;
            let rest_sy = rest.rest_scale_y;

            armature.bones[bone_idx].local_x = x - rest_x;
            armature.bones[bone_idx].local_y = y - rest_y;
            armature.bones[bone_idx].local_rotation = rotation - rest_rot;
            armature.bones[bone_idx].local_scale_x = scale_x - rest_sx;
            armature.bones[bone_idx].local_scale_y = scale_y - rest_sy;
        }

        // Evaluate slot timelines
        for (slot_name, timeline) in &clip.slot_timelines {
            let slot_idx = match armature.slots.iter().position(|s| s.name == *slot_name) {
                Some(i) => i,
                None => continue,
            };

            if timeline.frames.is_empty() {
                continue;
            }

            let (kf_a, kf_b, local_t) = find_slot_frame_pair(&timeline.frames, t, duration);
            let eased_t = apply_easing(local_t, kf_a.easing);
            let alpha = lerp(kf_a.alpha, kf_b.alpha, eased_t);

            armature.slots[slot_idx].color_alpha = alpha;

            // Display index: use the outgoing frame's value (no interpolation)
            armature.slots[slot_idx].display_index = kf_a.display_index.unwrap_or(-1);
        }

        // Recompute world transforms
        armature.update_world_transforms();
    }
}

/// Find the current frame pair and local interpolation parameter for bone timelines.
fn find_bone_frame_pair(
    frames: &[BoneKeyframe],
    time: f32,
    _total_duration: f32,
) -> (&BoneKeyframe, &BoneKeyframe, f32) {
    let mut accum = 0.0f32;
    for i in 0..frames.len() {
        let frame_end = accum + frames[i].duration;
        if time < frame_end || i == frames.len() - 1 {
            let next_idx = (i + 1) % frames.len();
            let local_t = if frames[i].duration > 0.0 {
                ((time - accum) / frames[i].duration).clamp(0.0, 1.0)
            } else {
                1.0
            };
            return (&frames[i], &frames[next_idx], local_t);
        }
        accum = frame_end;
    }
    // Fallback
    (&frames[0], &frames[0], 0.0)
}

/// Find the current frame pair and local interpolation parameter for slot timelines.
fn find_slot_frame_pair(
    frames: &[SlotKeyframe],
    time: f32,
    _total_duration: f32,
) -> (&SlotKeyframe, &SlotKeyframe, f32) {
    let mut accum = 0.0f32;
    for i in 0..frames.len() {
        let frame_end = accum + frames[i].duration;
        if time < frame_end || i == frames.len() - 1 {
            let next_idx = (i + 1) % frames.len();
            let local_t = if frames[i].duration > 0.0 {
                ((time - accum) / frames[i].duration).clamp(0.0, 1.0)
            } else {
                1.0
            };
            return (&frames[i], &frames[next_idx], local_t);
        }
        accum = frame_end;
    }
    (&frames[0], &frames[0], 0.0)
}

/// Linear interpolation.
fn lerp(a: f32, b: f32, t: f32) -> f32 {
    a + (b - a) * t
}

/// Angular interpolation with wrap-around.
fn lerp_angle(a: f32, b: f32, t: f32) -> f32 {
    let mut diff = b - a;
    // Normalize to [-PI, PI]
    while diff > std::f32::consts::PI {
        diff -= 2.0 * std::f32::consts::PI;
    }
    while diff < -std::f32::consts::PI {
        diff += 2.0 * std::f32::consts::PI;
    }
    a + diff * t
}

/// Apply easing. For MVP, passthrough (linear).
fn apply_easing(t: f32, _easing: Option<f32>) -> f32 {
    // Passthrough for now — could implement quadratic/cubic easing later
    let _ = _easing;
    t
}
