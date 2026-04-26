use crate::combat::hitbox::HitShape;

#[derive(Clone, Debug)]
pub struct AttackFrameData {
    pub animation_name: String,
    pub stamina_cost: f32,
    pub hitboxes: Vec<(u32, HitboxDef)>,
    pub cancel_window_start: u32,
    pub cancel_window_end: u32,
    pub recovery_frames: u32,
    pub poise_frames_start: Option<u32>,
    pub poise_frames_end: Option<u32>,
    pub lunge_speed: f32,
    pub lunge_duration_frames: u32,
}

#[derive(Clone, Debug)]
pub struct HitboxDef {
    pub shape: HitShape,
    pub damage: i32,
    pub knockback: f32,
    pub poise_damage: f32,
}

pub trait WeaponMoveset {
    fn light_attack_chain(&self) -> Vec<AttackFrameData>;
    fn heavy_attack(&self) -> AttackFrameData;
    fn running_attack(&self) -> AttackFrameData;
    fn rolling_attack(&self) -> AttackFrameData;
    fn backstab(&self) -> AttackFrameData;
    fn parry(&self) -> Option<AttackFrameData>;
}

pub struct LongswordMoveset;

impl WeaponMoveset for LongswordMoveset {
    fn light_attack_chain(&self) -> Vec<AttackFrameData> {
        vec![
            AttackFrameData {
                animation_name: "light_1".into(),
                stamina_cost: 20.0,
                hitboxes: vec![(
                    4,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 24.0, half_h: 12.0, offset_x: 20.0, offset_y: 0.0 },
                        damage: 80,
                        knockback: 3.0,
                        poise_damage: 15.0,
                    },
                )],
                cancel_window_start: 10,
                cancel_window_end: 16,
                recovery_frames: 18,
                poise_frames_start: Some(3),
                poise_frames_end: Some(12),
                lunge_speed: 60.0,
                lunge_duration_frames: 4,
            },
            AttackFrameData {
                animation_name: "light_2".into(),
                stamina_cost: 22.0,
                hitboxes: vec![(
                    3,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 28.0, half_h: 14.0, offset_x: 22.0, offset_y: 0.0 },
                        damage: 95,
                        knockback: 4.0,
                        poise_damage: 20.0,
                    },
                )],
                cancel_window_start: 8,
                cancel_window_end: 14,
                recovery_frames: 16,
                poise_frames_start: Some(2),
                poise_frames_end: Some(10),
                lunge_speed: 70.0,
                lunge_duration_frames: 3,
            },
        ]
    }

    fn heavy_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "heavy".into(),
            stamina_cost: 35.0,
            hitboxes: vec![(
                8,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 32.0, half_h: 16.0, offset_x: 24.0, offset_y: 0.0 },
                    damage: 150,
                    knockback: 6.0,
                    poise_damage: 30.0,
                },
            )],
            cancel_window_start: 16,
            cancel_window_end: 22,
            recovery_frames: 26,
            poise_frames_start: Some(6),
            poise_frames_end: Some(18),
            lunge_speed: 40.0,
            lunge_duration_frames: 6,
        }
    }

    fn running_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "running".into(),
            stamina_cost: 25.0,
            hitboxes: vec![(
                3,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 20.0, half_h: 12.0, offset_x: 18.0, offset_y: 0.0 },
                    damage: 90,
                    knockback: 5.0,
                    poise_damage: 18.0,
                },
            )],
            cancel_window_start: 8,
            cancel_window_end: 14,
            recovery_frames: 16,
            poise_frames_start: Some(2),
            poise_frames_end: Some(8),
            lunge_speed: 100.0,
            lunge_duration_frames: 5,
        }
    }

    fn rolling_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "rolling_attack".into(),
            stamina_cost: 20.0,
            hitboxes: vec![(
                5,
                HitboxDef {
                    shape: HitShape::Circle { radius: 20.0, offset_x: 16.0, offset_y: 0.0 },
                    damage: 85,
                    knockback: 4.0,
                    poise_damage: 16.0,
                },
            )],
            cancel_window_start: 10,
            cancel_window_end: 16,
            recovery_frames: 18,
            poise_frames_start: Some(4),
            poise_frames_end: Some(12),
            lunge_speed: 80.0,
            lunge_duration_frames: 4,
        }
    }

    fn backstab(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "backstab".into(),
            stamina_cost: 30.0,
            hitboxes: vec![],
            cancel_window_start: 20,
            cancel_window_end: 24,
            recovery_frames: 28,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        }
    }

    fn parry(&self) -> Option<AttackFrameData> {
        Some(AttackFrameData {
            animation_name: "parry".into(),
            stamina_cost: 15.0,
            hitboxes: vec![(
                3,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 16.0, half_h: 20.0, offset_x: 14.0, offset_y: 0.0 },
                    damage: 0,
                    knockback: 0.0,
                    poise_damage: 0.0,
                },
            )],
            cancel_window_start: 6,
            cancel_window_end: 10,
            recovery_frames: 20,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        })
    }
}
