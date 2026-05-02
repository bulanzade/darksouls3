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

pub struct FistMoveset;

impl WeaponMoveset for FistMoveset {
    fn light_attack_chain(&self) -> Vec<AttackFrameData> {
        vec![
            AttackFrameData {
                animation_name: "punch_1".into(),
                stamina_cost: 8.0,
                hitboxes: vec![(
                    2,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 10.0, half_h: 10.0, offset_x: 12.0, offset_y: 0.0 },
                        damage: 15,
                        knockback: 1.0,
                        poise_damage: 3.0,
                    },
                )],
                cancel_window_start: 3,
                cancel_window_end: 6,
                recovery_frames: 8,
                poise_frames_start: Some(1),
                poise_frames_end: Some(4),
                lunge_speed: 80.0,
                lunge_duration_frames: 2,
            },
            AttackFrameData {
                animation_name: "punch_2".into(),
                stamina_cost: 10.0,
                hitboxes: vec![(
                    2,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 10.0, half_h: 10.0, offset_x: 12.0, offset_y: 0.0 },
                        damage: 20,
                        knockback: 1.5,
                        poise_damage: 4.0,
                    },
                )],
                cancel_window_start: 3,
                cancel_window_end: 5,
                recovery_frames: 7,
                poise_frames_start: Some(1),
                poise_frames_end: Some(3),
                lunge_speed: 90.0,
                lunge_duration_frames: 2,
            },
        ]
    }

    fn heavy_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "heavy_punch".into(),
            stamina_cost: 12.0,
            hitboxes: vec![(
                4,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 12.0, half_h: 12.0, offset_x: 14.0, offset_y: 0.0 },
                    damage: 25,
                    knockback: 2.0,
                    poise_damage: 6.0,
                },
            )],
            cancel_window_start: 6,
            cancel_window_end: 9,
            recovery_frames: 12,
            poise_frames_start: Some(2),
            poise_frames_end: Some(6),
            lunge_speed: 50.0,
            lunge_duration_frames: 3,
        }
    }

    fn running_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "jumping_fist".into(),
            stamina_cost: 10.0,
            hitboxes: vec![(
                3,
                HitboxDef {
                    shape: HitShape::Circle { radius: 12.0, offset_x: 10.0, offset_y: 0.0 },
                    damage: 20,
                    knockback: 2.0,
                    poise_damage: 5.0,
                },
            )],
            cancel_window_start: 4,
            cancel_window_end: 7,
            recovery_frames: 10,
            poise_frames_start: Some(1),
            poise_frames_end: Some(4),
            lunge_speed: 100.0,
            lunge_duration_frames: 3,
        }
    }

    fn rolling_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "rolling_punch".into(),
            stamina_cost: 8.0,
            hitboxes: vec![(
                3,
                HitboxDef {
                    shape: HitShape::Circle { radius: 10.0, offset_x: 10.0, offset_y: 0.0 },
                    damage: 18,
                    knockback: 1.5,
                    poise_damage: 4.0,
                },
            )],
            cancel_window_start: 4,
            cancel_window_end: 7,
            recovery_frames: 10,
            poise_frames_start: Some(1),
            poise_frames_end: Some(4),
            lunge_speed: 70.0,
            lunge_duration_frames: 2,
        }
    }

    fn backstab(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "backstab".into(),
            stamina_cost: 15.0,
            hitboxes: vec![],
            cancel_window_start: 10,
            cancel_window_end: 14,
            recovery_frames: 16,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        }
    }

    fn parry(&self) -> Option<AttackFrameData> {
        Some(AttackFrameData {
            animation_name: "fist_parry".into(),
            stamina_cost: 8.0,
            hitboxes: vec![(
                2,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 12.0, half_h: 16.0, offset_x: 10.0, offset_y: 0.0 },
                    damage: 0,
                    knockback: 0.0,
                    poise_damage: 0.0,
                },
            )],
            cancel_window_start: 3,
            cancel_window_end: 5,
            recovery_frames: 16,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        })
    }
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

pub struct GreatAxeMoveset;

impl WeaponMoveset for GreatAxeMoveset {
    fn light_attack_chain(&self) -> Vec<AttackFrameData> {
        vec![
            AttackFrameData {
                animation_name: "heavy_swing_1".into(),
                stamina_cost: 30.0,
                hitboxes: vec![(
                    6,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 36.0, half_h: 20.0, offset_x: 24.0, offset_y: 0.0 },
                        damage: 130,
                        knockback: 8.0,
                        poise_damage: 35.0,
                    },
                )],
                cancel_window_start: 14,
                cancel_window_end: 20,
                recovery_frames: 28,
                poise_frames_start: Some(4),
                poise_frames_end: Some(14),
                lunge_speed: 30.0,
                lunge_duration_frames: 6,
            },
            AttackFrameData {
                animation_name: "heavy_swing_2".into(),
                stamina_cost: 35.0,
                hitboxes: vec![(
                    5,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 40.0, half_h: 22.0, offset_x: 26.0, offset_y: 0.0 },
                        damage: 160,
                        knockback: 10.0,
                        poise_damage: 40.0,
                    },
                )],
                cancel_window_start: 12,
                cancel_window_end: 18,
                recovery_frames: 30,
                poise_frames_start: Some(3),
                poise_frames_end: Some(12),
                lunge_speed: 25.0,
                lunge_duration_frames: 5,
            },
        ]
    }

    fn heavy_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "smash".into(),
            stamina_cost: 50.0,
            hitboxes: vec![(
                10,
                HitboxDef {
                    shape: HitShape::Circle { radius: 40.0, offset_x: 20.0, offset_y: 0.0 },
                    damage: 200,
                    knockback: 12.0,
                    poise_damage: 50.0,
                },
            )],
            cancel_window_start: 20,
            cancel_window_end: 28,
            recovery_frames: 36,
            poise_frames_start: Some(8),
            poise_frames_end: Some(22),
            lunge_speed: 20.0,
            lunge_duration_frames: 8,
        }
    }

    fn running_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "running_smash".into(),
            stamina_cost: 35.0,
            hitboxes: vec![(
                5,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 34.0, half_h: 18.0, offset_x: 22.0, offset_y: 0.0 },
                    damage: 140,
                    knockback: 9.0,
                    poise_damage: 38.0,
                },
            )],
            cancel_window_start: 12,
            cancel_window_end: 18,
            recovery_frames: 26,
            poise_frames_start: Some(3),
            poise_frames_end: Some(10),
            lunge_speed: 70.0,
            lunge_duration_frames: 5,
        }
    }

    fn rolling_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "rolling_smash".into(),
            stamina_cost: 30.0,
            hitboxes: vec![(
                6,
                HitboxDef {
                    shape: HitShape::Circle { radius: 30.0, offset_x: 16.0, offset_y: 0.0 },
                    damage: 120,
                    knockback: 7.0,
                    poise_damage: 30.0,
                },
            )],
            cancel_window_start: 12,
            cancel_window_end: 18,
            recovery_frames: 24,
            poise_frames_start: Some(4),
            poise_frames_end: Some(12),
            lunge_speed: 60.0,
            lunge_duration_frames: 4,
        }
    }

    fn backstab(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "backstab".into(),
            stamina_cost: 40.0,
            hitboxes: vec![],
            cancel_window_start: 18,
            cancel_window_end: 24,
            recovery_frames: 30,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        }
    }

    fn parry(&self) -> Option<AttackFrameData> { None }
}

pub struct DaggerMoveset;

impl WeaponMoveset for DaggerMoveset {
    fn light_attack_chain(&self) -> Vec<AttackFrameData> {
        vec![
            AttackFrameData {
                animation_name: "quick_slash_1".into(),
                stamina_cost: 12.0,
                hitboxes: vec![(
                    2,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 16.0, half_h: 10.0, offset_x: 14.0, offset_y: 0.0 },
                        damage: 45,
                        knockback: 1.5,
                        poise_damage: 5.0,
                    },
                )],
                cancel_window_start: 5,
                cancel_window_end: 8,
                recovery_frames: 10,
                poise_frames_start: Some(1),
                poise_frames_end: Some(4),
                lunge_speed: 80.0,
                lunge_duration_frames: 2,
            },
            AttackFrameData {
                animation_name: "quick_slash_2".into(),
                stamina_cost: 14.0,
                hitboxes: vec![(
                    2,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 18.0, half_h: 10.0, offset_x: 15.0, offset_y: 0.0 },
                        damage: 55,
                        knockback: 2.0,
                        poise_damage: 6.0,
                    },
                )],
                cancel_window_start: 4,
                cancel_window_end: 7,
                recovery_frames: 9,
                poise_frames_start: Some(1),
                poise_frames_end: Some(3),
                lunge_speed: 90.0,
                lunge_duration_frames: 2,
            },
            AttackFrameData {
                animation_name: "quick_slash_3".into(),
                stamina_cost: 16.0,
                hitboxes: vec![(
                    2,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 16.0, half_h: 12.0, offset_x: 14.0, offset_y: 0.0 },
                        damage: 65,
                        knockback: 3.0,
                        poise_damage: 8.0,
                    },
                )],
                cancel_window_start: 4,
                cancel_window_end: 7,
                recovery_frames: 10,
                poise_frames_start: Some(1),
                poise_frames_end: Some(3),
                lunge_speed: 100.0,
                lunge_duration_frames: 2,
            },
        ]
    }

    fn heavy_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "riposte".into(),
            stamina_cost: 20.0,
            hitboxes: vec![(
                4,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 14.0, half_h: 12.0, offset_x: 12.0, offset_y: 0.0 },
                    damage: 120,
                    knockback: 3.0,
                    poise_damage: 10.0,
                },
            )],
            cancel_window_start: 8,
            cancel_window_end: 12,
            recovery_frames: 14,
            poise_frames_start: Some(2),
            poise_frames_end: Some(6),
            lunge_speed: 50.0,
            lunge_duration_frames: 3,
        }
    }

    fn running_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "dash_stab".into(),
            stamina_cost: 18.0,
            hitboxes: vec![(
                2,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 20.0, half_h: 8.0, offset_x: 18.0, offset_y: 0.0 },
                    damage: 60,
                    knockback: 2.0,
                    poise_damage: 7.0,
                },
            )],
            cancel_window_start: 5,
            cancel_window_end: 8,
            recovery_frames: 10,
            poise_frames_start: Some(1),
            poise_frames_end: Some(4),
            lunge_speed: 120.0,
            lunge_duration_frames: 3,
        }
    }

    fn rolling_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "rolling_slash".into(),
            stamina_cost: 14.0,
            hitboxes: vec![(
                3,
                HitboxDef {
                    shape: HitShape::Circle { radius: 16.0, offset_x: 12.0, offset_y: 0.0 },
                    damage: 55,
                    knockback: 2.0,
                    poise_damage: 6.0,
                },
            )],
            cancel_window_start: 6,
            cancel_window_end: 9,
            recovery_frames: 12,
            poise_frames_start: Some(2),
            poise_frames_end: Some(6),
            lunge_speed: 70.0,
            lunge_duration_frames: 3,
        }
    }

    fn backstab(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "backstab".into(),
            stamina_cost: 20.0,
            hitboxes: vec![],
            cancel_window_start: 14,
            cancel_window_end: 18,
            recovery_frames: 20,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        }
    }

    fn parry(&self) -> Option<AttackFrameData> {
        Some(AttackFrameData {
            animation_name: "parry".into(),
            stamina_cost: 10.0,
            hitboxes: vec![(
                2,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 14.0, half_h: 18.0, offset_x: 12.0, offset_y: 0.0 },
                    damage: 0,
                    knockback: 0.0,
                    poise_damage: 0.0,
                },
            )],
            cancel_window_start: 4,
            cancel_window_end: 7,
            recovery_frames: 14,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        })
    }
}

pub struct SpearMoveset;

impl WeaponMoveset for SpearMoveset {
    fn light_attack_chain(&self) -> Vec<AttackFrameData> {
        vec![
            AttackFrameData {
                animation_name: "thrust_1".into(),
                stamina_cost: 18.0,
                hitboxes: vec![(
                    3,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 10.0, half_h: 8.0, offset_x: 34.0, offset_y: 0.0 },
                        damage: 70,
                        knockback: 4.0,
                        poise_damage: 12.0,
                    },
                )],
                cancel_window_start: 7,
                cancel_window_end: 11,
                recovery_frames: 14,
                poise_frames_start: Some(2),
                poise_frames_end: Some(8),
                lunge_speed: 70.0,
                lunge_duration_frames: 3,
            },
            AttackFrameData {
                animation_name: "thrust_2".into(),
                stamina_cost: 20.0,
                hitboxes: vec![(
                    3,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 10.0, half_h: 8.0, offset_x: 36.0, offset_y: 0.0 },
                        damage: 85,
                        knockback: 5.0,
                        poise_damage: 14.0,
                    },
                )],
                cancel_window_start: 6,
                cancel_window_end: 10,
                recovery_frames: 13,
                poise_frames_start: Some(2),
                poise_frames_end: Some(7),
                lunge_speed: 80.0,
                lunge_duration_frames: 3,
            },
        ]
    }

    fn heavy_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "charge_thrust".into(),
            stamina_cost: 35.0,
            hitboxes: vec![(
                7,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 12.0, half_h: 10.0, offset_x: 40.0, offset_y: 0.0 },
                    damage: 140,
                    knockback: 8.0,
                    poise_damage: 25.0,
                },
            )],
            cancel_window_start: 14,
            cancel_window_end: 20,
            recovery_frames: 24,
            poise_frames_start: Some(4),
            poise_frames_end: Some(14),
            lunge_speed: 50.0,
            lunge_duration_frames: 7,
        }
    }

    fn running_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "sprint_thrust".into(),
            stamina_cost: 22.0,
            hitboxes: vec![(
                3,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 10.0, half_h: 8.0, offset_x: 38.0, offset_y: 0.0 },
                    damage: 90,
                    knockback: 6.0,
                    poise_damage: 16.0,
                },
            )],
            cancel_window_start: 6,
            cancel_window_end: 10,
            recovery_frames: 14,
            poise_frames_start: Some(2),
            poise_frames_end: Some(6),
            lunge_speed: 110.0,
            lunge_duration_frames: 4,
        }
    }

    fn rolling_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "rolling_thrust".into(),
            stamina_cost: 18.0,
            hitboxes: vec![(
                4,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 10.0, half_h: 8.0, offset_x: 32.0, offset_y: 0.0 },
                    damage: 75,
                    knockback: 4.0,
                    poise_damage: 12.0,
                },
            )],
            cancel_window_start: 8,
            cancel_window_end: 12,
            recovery_frames: 16,
            poise_frames_start: Some(3),
            poise_frames_end: Some(8),
            lunge_speed: 60.0,
            lunge_duration_frames: 4,
        }
    }

    fn backstab(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "backstab".into(),
            stamina_cost: 25.0,
            hitboxes: vec![],
            cancel_window_start: 16,
            cancel_window_end: 20,
            recovery_frames: 24,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        }
    }

    fn parry(&self) -> Option<AttackFrameData> { None }
}

pub struct UchigatanaMoveset;

impl WeaponMoveset for UchigatanaMoveset {
    fn light_attack_chain(&self) -> Vec<AttackFrameData> {
        vec![
            AttackFrameData {
                animation_name: "slash_1".into(),
                stamina_cost: 18.0,
                hitboxes: vec![(
                    3,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 26.0, half_h: 14.0, offset_x: 20.0, offset_y: 0.0 },
                        damage: 95,
                        knockback: 4.0,
                        poise_damage: 14.0,
                    },
                )],
                cancel_window_start: 7,
                cancel_window_end: 11,
                recovery_frames: 14,
                poise_frames_start: Some(2),
                poise_frames_end: Some(8),
                lunge_speed: 65.0,
                lunge_duration_frames: 3,
            },
            AttackFrameData {
                animation_name: "slash_2".into(),
                stamina_cost: 20.0,
                hitboxes: vec![(
                    3,
                    HitboxDef {
                        shape: HitShape::Rect { half_w: 28.0, half_h: 14.0, offset_x: 22.0, offset_y: 0.0 },
                        damage: 110,
                        knockback: 5.0,
                        poise_damage: 16.0,
                    },
                )],
                cancel_window_start: 6,
                cancel_window_end: 10,
                recovery_frames: 13,
                poise_frames_start: Some(2),
                poise_frames_end: Some(7),
                lunge_speed: 75.0,
                lunge_duration_frames: 3,
            },
        ]
    }

    fn heavy_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "draw_slash".into(),
            stamina_cost: 40.0,
            hitboxes: vec![(
                8,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 34.0, half_h: 18.0, offset_x: 22.0, offset_y: 0.0 },
                    damage: 170,
                    knockback: 7.0,
                    poise_damage: 28.0,
                },
            )],
            cancel_window_start: 16,
            cancel_window_end: 22,
            recovery_frames: 26,
            poise_frames_start: Some(5),
            poise_frames_end: Some(16),
            lunge_speed: 45.0,
            lunge_duration_frames: 6,
        }
    }

    fn running_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "running_slash".into(),
            stamina_cost: 22.0,
            hitboxes: vec![(
                3,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 24.0, half_h: 14.0, offset_x: 20.0, offset_y: 0.0 },
                    damage: 100,
                    knockback: 5.0,
                    poise_damage: 16.0,
                },
            )],
            cancel_window_start: 6,
            cancel_window_end: 10,
            recovery_frames: 14,
            poise_frames_start: Some(2),
            poise_frames_end: Some(6),
            lunge_speed: 100.0,
            lunge_duration_frames: 4,
        }
    }

    fn rolling_attack(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "rolling_slash".into(),
            stamina_cost: 18.0,
            hitboxes: vec![(
                4,
                HitboxDef {
                    shape: HitShape::Circle { radius: 22.0, offset_x: 16.0, offset_y: 0.0 },
                    damage: 90,
                    knockback: 4.0,
                    poise_damage: 14.0,
                },
            )],
            cancel_window_start: 8,
            cancel_window_end: 12,
            recovery_frames: 16,
            poise_frames_start: Some(3),
            poise_frames_end: Some(8),
            lunge_speed: 70.0,
            lunge_duration_frames: 4,
        }
    }

    fn backstab(&self) -> AttackFrameData {
        AttackFrameData {
            animation_name: "backstab".into(),
            stamina_cost: 28.0,
            hitboxes: vec![],
            cancel_window_start: 16,
            cancel_window_end: 20,
            recovery_frames: 24,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        }
    }

    fn parry(&self) -> Option<AttackFrameData> {
        Some(AttackFrameData {
            animation_name: "parry".into(),
            stamina_cost: 12.0,
            hitboxes: vec![(
                3,
                HitboxDef {
                    shape: HitShape::Rect { half_w: 16.0, half_h: 20.0, offset_x: 14.0, offset_y: 0.0 },
                    damage: 0,
                    knockback: 0.0,
                    poise_damage: 0.0,
                },
            )],
            cancel_window_start: 5,
            cancel_window_end: 8,
            recovery_frames: 16,
            poise_frames_start: None,
            poise_frames_end: None,
            lunge_speed: 0.0,
            lunge_duration_frames: 0,
        })
    }
}
