use crate::ai::aggro::AggroTable;
use crate::ai::boss_ai::{BossController, BossDirective, BossPhase};
use crate::core::transform::Transform;
use crate::entity::entity_trait::{DamageInfo, DamageOutcome, Entity, EntityId, EntityState};
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use web_sys::WebGl2RenderingContext as GL;

#[derive(Clone, Copy, PartialEq)]
pub enum BossType {
    IudexGundyr,
    Vordt,
    Dancer,
    CurseRottedGreatwood,
    CrystalSage,
    AbyssWatchers,
    HighLordWolnir,
    OldDemonKing,
    DeaconsOfTheDeep,
    PontiffSulyvahn,
    Yhorm,
    Aldrich,
    DragonslayerArmour,
    TwinPrinces,
    SoulOfCinder,
    Oceiros,
    ChampionGundyr,
    NamelessKing,
}

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum BossAttack {
    // Gundyr
    HalberdOverhead,    // 戟下砸 — windup then slam forward
    ShoulderCharge,     // 铁山靠 — fast dash into player
    HalberdSweep,       // 戟横扫 — wide horizontal swing
    // Vordt
    IceMaceCharge,      // 冰锤冲锋 — rush forward with ice mace
    IceBreadth,         // 冰息 — short range cone spray (damage + slow visual)
    LeapingSlam,        // 跳砸 — jump up and slam down
    // Curse-rotted Greatwood
    GroundSlam,
    SweepAttack,
    BodySlam,
    // Deacons of the Deep
    FlameBurst,
    ChargeAttack,
    HolyGround,
    // Pontiff Sulyvahn
    ComboSlash,
    ThrustAttack,
    ShadowClone,
}

pub struct Boss {
    pub id: EntityId,
    pub transform: Transform,
    pub hp: i32,
    pub max_hp: i32,
    pub speed: f32,
    pub state: EntityState,
    pub facing: f32,
    pub damage: i32,
    pub boss_ctrl: BossController,
    pub aggro: AggroTable,
    pub attack_timer: f32,
    pub attack_duration: f32,
    pub stagger_timer: f32,
    pub has_hit_this_attack: bool,
    pub last_hit_window: u8,
    pub flash_timer: f32,
    pub is_charging: bool,
    pub charge_speed: f32,
    pub boss_type: BossType,
    pub name: String,
    pub boss_activated: bool,
    pub current_attack: BossAttack,
    pub attack_hit_range: f32,
    attack_index: u32,
}

impl Boss {
    pub fn attack_progress(&self) -> f32 {
        if self.attack_duration <= 0.0 {
            return 0.0;
        }
        (1.0 - self.attack_timer / self.attack_duration).clamp(0.0, 1.0)
    }

    pub fn current_attack_can_be_parried(&self) -> bool {
        matches!(
            self.current_attack,
            BossAttack::HalberdOverhead
                | BossAttack::ShoulderCharge
                | BossAttack::HalberdSweep
                | BossAttack::IceMaceCharge
                | BossAttack::ChargeAttack
                | BossAttack::ComboSlash
                | BossAttack::ThrustAttack
        )
    }

    pub fn current_attack_can_hit(&self, target_x: f32, target_y: f32) -> bool {
        if self.state != EntityState::Attacking {
            return false;
        }

        let t = self.attack_progress();
        let window = self.current_hit_window(t);
        if window == 0 || self.last_hit_window == window {
            return false;
        }

        let dx = target_x - self.transform.x;
        let dy = target_y - self.transform.y;
        let dist_sq = dx * dx + dy * dy;
        let forward = dx * self.facing.cos() + dy * self.facing.sin();
        let side = -dx * self.facing.sin() + dy * self.facing.cos();

        match self.current_attack {
            BossAttack::HalberdOverhead => in_front(forward, side, -10.0, 95.0, 32.0),
            BossAttack::ShoulderCharge => in_front(forward, side, -18.0, 74.0, 38.0),
            BossAttack::HalberdSweep => dist_sq <= 108.0 * 108.0 && forward > -38.0,
            BossAttack::IceMaceCharge => in_front(forward, side, -14.0, 92.0, 44.0),
            BossAttack::IceBreadth => forward > 8.0 && forward < 132.0 && side.abs() < forward * 0.55 + 20.0,
            BossAttack::LeapingSlam => dist_sq <= 116.0 * 116.0,
            BossAttack::GroundSlam => dist_sq <= 110.0 * 110.0,
            BossAttack::SweepAttack => dist_sq <= 104.0 * 104.0 && forward > -42.0,
            BossAttack::BodySlam => in_front(forward, side, -8.0, 105.0, 58.0),
            BossAttack::FlameBurst => forward > 32.0 && forward < 178.0 && side.abs() < 30.0 + forward * 0.12,
            BossAttack::ChargeAttack => in_front(forward, side, -14.0, 88.0, 36.0),
            BossAttack::HolyGround => dist_sq <= 126.0 * 126.0,
            BossAttack::ComboSlash => dist_sq <= 82.0 * 82.0 && forward > -24.0 && side.abs() < 72.0,
            BossAttack::ThrustAttack => in_front(forward, side, 12.0, 150.0, 26.0),
            BossAttack::ShadowClone => {
                in_front(forward, side, 10.0, 112.0, 42.0)
                    || in_front(forward, side, 42.0, 150.0, 56.0)
            }
        }
    }

    pub fn mark_current_hit_window(&mut self) {
        self.last_hit_window = self.current_hit_window(self.attack_progress());
        self.has_hit_this_attack = true;
    }

    fn current_hit_window(&self, t: f32) -> u8 {
        // Multi-hit attacks reserve distinct window ids; all single-hit attacks use window 1.
        // Add extra guarded arms before the single-hit arms when introducing another multi-hit move.
        match self.current_attack {
            BossAttack::ComboSlash if (0.18..=0.38).contains(&t) => 1,
            BossAttack::ComboSlash if (0.56..=0.80).contains(&t) => 2,
            BossAttack::HalberdOverhead if (0.44..=0.68).contains(&t) => 1,
            BossAttack::ShoulderCharge if (0.16..=0.88).contains(&t) => 1,
            BossAttack::HalberdSweep if (0.34..=0.78).contains(&t) => 1,
            BossAttack::IceMaceCharge if (0.20..=0.90).contains(&t) => 1,
            BossAttack::IceBreadth if (0.38..=0.96).contains(&t) => 1,
            BossAttack::LeapingSlam if (0.54..=0.78).contains(&t) => 1,
            BossAttack::GroundSlam if (0.44..=0.70).contains(&t) => 1,
            BossAttack::SweepAttack if (0.30..=0.74).contains(&t) => 1,
            BossAttack::BodySlam if (0.52..=0.82).contains(&t) => 1,
            BossAttack::FlameBurst if (0.42..=0.76).contains(&t) => 1,
            BossAttack::ChargeAttack if (0.16..=0.88).contains(&t) => 1,
            BossAttack::HolyGround if (0.54..=0.78).contains(&t) => 1,
            BossAttack::ThrustAttack if (0.34..=0.72).contains(&t) => 1,
            BossAttack::ShadowClone if (0.54..=0.86).contains(&t) => 1,
            _ => 0,
        }
    }

    fn choose_attack(&mut self, dist: f32) -> BossAttack {
        let phase = self.boss_ctrl.current_phase_index();
        let seq = self.attack_index;
        self.attack_index += 1;

        match self.boss_type {
            BossType::IudexGundyr => {
                if dist > 118.0 {
                    BossAttack::ShoulderCharge
                } else if phase > 0 && seq % 3 != 1 {
                    BossAttack::HalberdSweep
                } else if seq % 2 == 0 {
                    BossAttack::HalberdOverhead
                } else {
                    BossAttack::HalberdSweep
                }
            }
            BossType::Vordt => {
                if phase > 0 && seq % 3 == 0 {
                    BossAttack::IceMaceCharge
                } else if dist < 82.0 {
                    BossAttack::IceBreadth
                } else if seq % 2 == 0 {
                    BossAttack::LeapingSlam
                } else {
                    BossAttack::IceMaceCharge
                }
            }
            BossType::Dancer => {
                if phase > 0 && seq % 4 == 0 {
                    BossAttack::LeapingSlam
                } else if dist < 60.0 {
                    BossAttack::ComboSlash
                } else if seq % 3 == 0 {
                    BossAttack::HalberdSweep
                } else {
                    BossAttack::ShoulderCharge
                }
            }
            BossType::CurseRottedGreatwood => {
                if dist > 105.0 {
                    BossAttack::BodySlam
                } else if phase > 1 || seq % 3 == 0 {
                    BossAttack::GroundSlam
                } else {
                    BossAttack::SweepAttack
                }
            }
            BossType::CrystalSage => {
                if dist > 120.0 {
                    BossAttack::FlameBurst
                } else if phase > 0 && seq % 3 == 0 {
                    BossAttack::HolyGround
                } else if seq % 2 == 0 {
                    BossAttack::ThrustAttack
                } else {
                    BossAttack::FlameBurst
                }
            }
            BossType::AbyssWatchers => {
                if seq % 4 == 0 {
                    BossAttack::ShoulderCharge
                } else if phase > 0 && seq % 3 == 0 {
                    BossAttack::HalberdSweep
                } else {
                    BossAttack::ComboSlash
                }
            }
            BossType::HighLordWolnir => {
                if dist > 130.0 {
                    BossAttack::FlameBurst
                } else if seq % 3 == 0 {
                    BossAttack::SweepAttack
                } else {
                    BossAttack::IceBreadth
                }
            }
            BossType::OldDemonKing => {
                if dist > 110.0 {
                    BossAttack::FlameBurst
                } else if phase > 0 && seq % 3 == 0 {
                    BossAttack::LeapingSlam
                } else {
                    BossAttack::GroundSlam
                }
            }
            BossType::DeaconsOfTheDeep => {
                if dist > 125.0 {
                    BossAttack::FlameBurst
                } else if phase > 0 && seq % 2 == 0 {
                    BossAttack::HolyGround
                } else {
                    BossAttack::ChargeAttack
                }
            }
            BossType::PontiffSulyvahn => {
                if phase > 0 && seq % 4 == 0 {
                    BossAttack::ShadowClone
                } else if dist > 86.0 {
                    BossAttack::ThrustAttack
                } else {
                    BossAttack::ComboSlash
                }
            }
            BossType::Yhorm => {
                if seq % 3 == 0 {
                    BossAttack::HalberdOverhead
                } else if phase > 0 && seq % 2 == 0 {
                    BossAttack::HolyGround
                } else {
                    BossAttack::GroundSlam
                }
            }
            BossType::Aldrich => {
                if dist > 100.0 {
                    BossAttack::FlameBurst
                } else if phase > 0 && seq % 4 == 0 {
                    BossAttack::ShadowClone
                } else {
                    BossAttack::ComboSlash
                }
            }
            BossType::DragonslayerArmour => {
                if dist > 100.0 {
                    BossAttack::IceMaceCharge
                } else if phase > 0 && seq % 3 == 0 {
                    BossAttack::HolyGround
                } else {
                    BossAttack::ShoulderCharge
                }
            }
            BossType::TwinPrinces => {
                if phase > 0 && seq % 4 == 0 {
                    BossAttack::ShadowClone
                } else if seq % 3 == 0 {
                    BossAttack::FlameBurst
                } else {
                    BossAttack::HalberdOverhead
                }
            }
            BossType::SoulOfCinder => {
                if phase > 1 {
                    BossAttack::HalberdSweep
                } else if dist > 110.0 {
                    BossAttack::FlameBurst
                } else if phase > 0 && seq % 3 == 0 {
                    BossAttack::HolyGround
                } else {
                    BossAttack::ComboSlash
                }
            }
            BossType::Oceiros => {
                if phase > 0 && seq % 3 == 0 {
                    BossAttack::HolyGround
                } else if dist > 90.0 {
                    BossAttack::ShoulderCharge
                } else {
                    BossAttack::HalberdSweep
                }
            }
            BossType::ChampionGundyr => {
                if phase > 0 && seq % 2 == 0 {
                    BossAttack::ComboSlash
                } else if dist > 80.0 {
                    BossAttack::ShoulderCharge
                } else {
                    BossAttack::HalberdOverhead
                }
            }
            BossType::NamelessKing => {
                if phase > 0 && seq % 3 == 0 {
                    BossAttack::HolyGround
                } else if dist > 120.0 {
                    BossAttack::ThrustAttack
                } else if phase > 0 && seq % 2 == 0 {
                    BossAttack::ComboSlash
                } else {
                    BossAttack::HalberdSweep
                }
            }
        }
    }

    pub fn new_curse_rotted_greatwood(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase {
                health_threshold: 1.0,
                speed_multiplier: 1.0,
                damage_multiplier: 1.0,
                attack_cooldown: 2.0,
                new_attack_damage: 30,
                phase_name: "Phase 1".into(),
            },
            BossPhase {
                health_threshold: 0.6,
                speed_multiplier: 1.2,
                damage_multiplier: 1.1,
                attack_cooldown: 1.8,
                new_attack_damage: 40,
                phase_name: "Phase 2".into(),
            },
            BossPhase {
                health_threshold: 0.3,
                speed_multiplier: 1.4,
                damage_multiplier: 1.2,
                attack_cooldown: 1.5,
                new_attack_damage: 50,
                phase_name: "Phase 3 - Berserk".into(),
            },
        ];

        Self {
            id,
            transform: Transform::new(x, y),
            hp: 1200,
            max_hp: 1200,
            speed: 40.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 60,
            boss_ctrl: BossController::new(phases),
            aggro: AggroTable::new(300.0, 500.0),
            attack_timer: 0.0,
            attack_duration: 0.8,
            stagger_timer: 0.0,
            has_hit_this_attack: false,
            last_hit_window: 0,
            flash_timer: 0.0,
            is_charging: false,
            charge_speed: 300.0,
            boss_type: BossType::CurseRottedGreatwood,
            name: "咒蚀大树".into(),
            boss_activated: false,
            current_attack: BossAttack::GroundSlam,
            attack_hit_range: 48.0,
            attack_index: 0,
        }
    }

    pub fn new_deacons_of_the_deep(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase {
                health_threshold: 1.0,
                speed_multiplier: 1.3,
                damage_multiplier: 1.0,
                attack_cooldown: 1.5,
                new_attack_damage: 40,
                phase_name: "Phase 1".into(),
            },
            BossPhase {
                health_threshold: 0.4,
                speed_multiplier: 1.6,
                damage_multiplier: 1.3,
                attack_cooldown: 1.0,
                new_attack_damage: 55,
                phase_name: "Phase 2 - Mounted Fury".into(),
            },
        ];

        Self {
            id,
            transform: Transform::new(x, y),
            hp: 1500,
            max_hp: 1500,
            speed: 55.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 50,
            boss_ctrl: BossController::new(phases),
            aggro: AggroTable::new(400.0, 600.0),
            attack_timer: 0.0,
            attack_duration: 0.6,
            stagger_timer: 0.0,
            has_hit_this_attack: false,
            last_hit_window: 0,
            flash_timer: 0.0,
            is_charging: false,
            charge_speed: 400.0,
            boss_type: BossType::DeaconsOfTheDeep,
            name: "幽邃主教群".into(),
            boss_activated: false,
            current_attack: BossAttack::GroundSlam,
            attack_hit_range: 48.0,
            attack_index: 0,
        }
    }

    pub fn new_pontiff_sulyvahn(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase {
                health_threshold: 1.0,
                speed_multiplier: 1.0,
                damage_multiplier: 1.0,
                attack_cooldown: 2.0,
                new_attack_damage: 35,
                phase_name: "Phase 1".into(),
            },
            BossPhase {
                health_threshold: 0.5,
                speed_multiplier: 1.5,
                damage_multiplier: 1.2,
                attack_cooldown: 1.2,
                new_attack_damage: 50,
                phase_name: "Phase 2 - Shield Break".into(),
            },
        ];

        Self {
            id,
            transform: Transform::new(x, y),
            hp: 1000,
            max_hp: 1000,
            speed: 50.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 45,
            boss_ctrl: BossController::new(phases),
            aggro: AggroTable::new(250.0, 450.0),
            attack_timer: 0.0,
            attack_duration: 0.7,
            stagger_timer: 0.0,
            has_hit_this_attack: false,
            last_hit_window: 0,
            flash_timer: 0.0,
            is_charging: false,
            charge_speed: 350.0,
            boss_type: BossType::PontiffSulyvahn,
            name: "教宗沙立万".into(),
            boss_activated: false,
            current_attack: BossAttack::GroundSlam,
            attack_hit_range: 48.0,
            attack_index: 0,
        }
    }

    pub fn new_iudex_gundyr(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase {
                health_threshold: 1.0,
                speed_multiplier: 1.0,
                damage_multiplier: 1.0,
                attack_cooldown: 2.5,
                new_attack_damage: 25,
                phase_name: "Phase 1".into(),
            },
            BossPhase {
                health_threshold: 0.5,
                speed_multiplier: 1.3,
                damage_multiplier: 1.2,
                attack_cooldown: 2.0,
                new_attack_damage: 40,
                phase_name: "Phase 2 - Pus of Man".into(),
            },
        ];

        Self {
            id,
            transform: Transform::new(x, y),
            hp: 800,
            max_hp: 800,
            speed: 35.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 35,
            boss_ctrl: BossController::new(phases),
            aggro: AggroTable::new(300.0, 500.0),
            attack_timer: 0.0,
            attack_duration: 0.8,
            stagger_timer: 0.0,
            has_hit_this_attack: false,
            last_hit_window: 0,
            flash_timer: 0.0,
            is_charging: false,
            charge_speed: 250.0,
            boss_type: BossType::IudexGundyr,
            name: "灰烬审判者古达".into(),
            boss_activated: false,
            current_attack: BossAttack::GroundSlam,
            attack_hit_range: 48.0,
            attack_index: 0,
        }
    }

    pub fn new_vordt(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase {
                health_threshold: 1.0,
                speed_multiplier: 1.1,
                damage_multiplier: 1.0,
                attack_cooldown: 2.0,
                new_attack_damage: 35,
                phase_name: "Phase 1".into(),
            },
            BossPhase {
                health_threshold: 0.4,
                speed_multiplier: 1.5,
                damage_multiplier: 1.3,
                attack_cooldown: 1.5,
                new_attack_damage: 50,
                phase_name: "Phase 2 - Beast".into(),
            },
        ];

        Self {
            id,
            transform: Transform::new(x, y),
            hp: 1100,
            max_hp: 1100,
            speed: 45.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 45,
            boss_ctrl: BossController::new(phases),
            aggro: AggroTable::new(350.0, 550.0),
            attack_timer: 0.0,
            attack_duration: 0.7,
            stagger_timer: 0.0,
            has_hit_this_attack: false,
            last_hit_window: 0,
            flash_timer: 0.0,
            is_charging: false,
            charge_speed: 300.0,
            boss_type: BossType::Vordt,
            name: "冷冽谷的波尔多".into(),
            boss_activated: false,
            current_attack: BossAttack::GroundSlam,
            attack_hit_range: 48.0,
            attack_index: 0,
        }
    }

    pub fn new_dancer(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 1.1, damage_multiplier: 1.0, attack_cooldown: 2.2, new_attack_damage: 40, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.5, speed_multiplier: 1.6, damage_multiplier: 1.3, attack_cooldown: 1.2, new_attack_damage: 55, phase_name: "Phase 2 - Grace".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 2600, max_hp: 2600, speed: 55.0,
            state: EntityState::Idle, facing: 0.0, damage: 40,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(300.0, 500.0),
            attack_timer: 0.0, attack_duration: 0.7, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 350.0,
            boss_type: BossType::Dancer, name: "舞娘".into(),
            boss_activated: false, current_attack: BossAttack::ComboSlash,
            attack_hit_range: 60.0, attack_index: 0,
        }
    }

    pub fn new_crystal_sage(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 0.9, damage_multiplier: 1.0, attack_cooldown: 2.5, new_attack_damage: 30, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.5, speed_multiplier: 1.3, damage_multiplier: 1.4, attack_cooldown: 1.5, new_attack_damage: 50, phase_name: "Phase 2 - Split".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 1200, max_hp: 1200, speed: 35.0,
            state: EntityState::Idle, facing: 0.0, damage: 35,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(350.0, 500.0),
            attack_timer: 0.0, attack_duration: 0.8, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 200.0,
            boss_type: BossType::CrystalSage, name: "结晶老者".into(),
            boss_activated: false, current_attack: BossAttack::FlameBurst,
            attack_hit_range: 48.0, attack_index: 0,
        }
    }

    pub fn new_abyss_watchers(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 1.2, damage_multiplier: 1.0, attack_cooldown: 1.8, new_attack_damage: 35, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.5, speed_multiplier: 1.6, damage_multiplier: 1.2, attack_cooldown: 1.0, new_attack_damage: 50, phase_name: "Phase 2 - Wolf Blood".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 1800, max_hp: 1800, speed: 65.0,
            state: EntityState::Idle, facing: 0.0, damage: 38,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(300.0, 550.0),
            attack_timer: 0.0, attack_duration: 0.6, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 350.0,
            boss_type: BossType::AbyssWatchers, name: "深渊监视者".into(),
            boss_activated: false, current_attack: BossAttack::ComboSlash,
            attack_hit_range: 55.0, attack_index: 0,
        }
    }

    pub fn new_high_lord_wolnir(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 0.8, damage_multiplier: 1.0, attack_cooldown: 2.5, new_attack_damage: 45, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.5, speed_multiplier: 1.2, damage_multiplier: 1.3, attack_cooldown: 1.8, new_attack_damage: 60, phase_name: "Phase 2 - Darkness".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 2000, max_hp: 2000, speed: 30.0,
            state: EntityState::Idle, facing: 0.0, damage: 50,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(400.0, 600.0),
            attack_timer: 0.0, attack_duration: 1.0, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 200.0,
            boss_type: BossType::HighLordWolnir, name: "霸王沃尼尔".into(),
            boss_activated: false, current_attack: BossAttack::SweepAttack,
            attack_hit_range: 70.0, attack_index: 0,
        }
    }

    pub fn new_old_demon_king(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 0.9, damage_multiplier: 1.0, attack_cooldown: 2.2, new_attack_damage: 45, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.4, speed_multiplier: 1.3, damage_multiplier: 1.4, attack_cooldown: 1.5, new_attack_damage: 60, phase_name: "Phase 2 - Fury".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 1900, max_hp: 1900, speed: 35.0,
            state: EntityState::Idle, facing: 0.0, damage: 50,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(350.0, 550.0),
            attack_timer: 0.0, attack_duration: 0.9, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 250.0,
            boss_type: BossType::OldDemonKing, name: "老恶魔王".into(),
            boss_activated: false, current_attack: BossAttack::GroundSlam,
            attack_hit_range: 60.0, attack_index: 0,
        }
    }

    pub fn new_yhorm(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 0.8, damage_multiplier: 1.0, attack_cooldown: 2.5, new_attack_damage: 55, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.5, speed_multiplier: 1.2, damage_multiplier: 1.3, attack_cooldown: 1.8, new_attack_damage: 70, phase_name: "Phase 2 - Rampage".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 2500, max_hp: 2500, speed: 30.0,
            state: EntityState::Idle, facing: 0.0, damage: 60,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(400.0, 600.0),
            attack_timer: 0.0, attack_duration: 1.0, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 200.0,
            boss_type: BossType::Yhorm, name: "罪业之都的王—尤姆".into(),
            boss_activated: false, current_attack: BossAttack::HalberdOverhead,
            attack_hit_range: 65.0, attack_index: 0,
        }
    }

    pub fn new_aldrich(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 0.9, damage_multiplier: 1.0, attack_cooldown: 2.0, new_attack_damage: 40, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.5, speed_multiplier: 1.3, damage_multiplier: 1.3, attack_cooldown: 1.4, new_attack_damage: 55, phase_name: "Phase 2 - Devourer".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 2400, max_hp: 2400, speed: 35.0,
            state: EntityState::Idle, facing: 0.0, damage: 45,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(350.0, 550.0),
            attack_timer: 0.0, attack_duration: 0.8, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 250.0,
            boss_type: BossType::Aldrich, name: "艾尔德里奇".into(),
            boss_activated: false, current_attack: BossAttack::FlameBurst,
            attack_hit_range: 55.0, attack_index: 0,
        }
    }

    pub fn new_dragonslayer_armour(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 1.0, damage_multiplier: 1.0, attack_cooldown: 2.0, new_attack_damage: 45, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.4, speed_multiplier: 1.5, damage_multiplier: 1.3, attack_cooldown: 1.3, new_attack_damage: 60, phase_name: "Phase 2 - Storm".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 2800, max_hp: 2800, speed: 40.0,
            state: EntityState::Idle, facing: 0.0, damage: 50,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(350.0, 550.0),
            attack_timer: 0.0, attack_duration: 0.8, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 300.0,
            boss_type: BossType::DragonslayerArmour, name: "猎龙铠甲".into(),
            boss_activated: false, current_attack: BossAttack::ShoulderCharge,
            attack_hit_range: 55.0, attack_index: 0,
        }
    }

    pub fn new_twin_princes(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 1.0, damage_multiplier: 1.0, attack_cooldown: 2.2, new_attack_damage: 45, phase_name: "Phase 1 - Lorian".into() },
            BossPhase { health_threshold: 0.5, speed_multiplier: 1.3, damage_multiplier: 1.3, attack_cooldown: 1.5, new_attack_damage: 60, phase_name: "Phase 2 - United".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 3200, max_hp: 3200, speed: 40.0,
            state: EntityState::Idle, facing: 0.0, damage: 50,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(300.0, 500.0),
            attack_timer: 0.0, attack_duration: 0.9, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 350.0,
            boss_type: BossType::TwinPrinces, name: "双子王子".into(),
            boss_activated: false, current_attack: BossAttack::HalberdOverhead,
            attack_hit_range: 55.0, attack_index: 0,
        }
    }

    pub fn new_soul_of_cinder(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 1.1, damage_multiplier: 1.0, attack_cooldown: 1.8, new_attack_damage: 45, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.6, speed_multiplier: 1.3, damage_multiplier: 1.2, attack_cooldown: 1.3, new_attack_damage: 55, phase_name: "Phase 2 - Magic".into() },
            BossPhase { health_threshold: 0.25, speed_multiplier: 1.6, damage_multiplier: 1.5, attack_cooldown: 0.9, new_attack_damage: 70, phase_name: "Phase 3 - Gwyn".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 4000, max_hp: 4000, speed: 50.0,
            state: EntityState::Idle, facing: 0.0, damage: 50,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(350.0, 550.0),
            attack_timer: 0.0, attack_duration: 0.7, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 350.0,
            boss_type: BossType::SoulOfCinder, name: "薪王们的化身".into(),
            boss_activated: false, current_attack: BossAttack::ComboSlash,
            attack_hit_range: 50.0, attack_index: 0,
        }
    }

    pub fn new_oceiros(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 1.1, damage_multiplier: 1.0, attack_cooldown: 2.0, new_attack_damage: 40, phase_name: "Phase 1 - Dragon".into() },
            BossPhase { health_threshold: 0.4, speed_multiplier: 1.5, damage_multiplier: 1.4, attack_cooldown: 1.2, new_attack_damage: 60, phase_name: "Phase 2 - Madness".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 3000, max_hp: 3000, speed: 50.0,
            state: EntityState::Idle, facing: 0.0, damage: 45,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(350.0, 550.0),
            attack_timer: 0.0, attack_duration: 0.8, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 350.0,
            boss_type: BossType::Oceiros, name: "妖王欧斯罗艾斯".into(),
            boss_activated: false, current_attack: BossAttack::ShoulderCharge,
            attack_hit_range: 60.0, attack_index: 0,
        }
    }

    pub fn new_champion_gundyr(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 1.2, damage_multiplier: 1.1, attack_cooldown: 1.8, new_attack_damage: 40, phase_name: "Phase 1".into() },
            BossPhase { health_threshold: 0.5, speed_multiplier: 1.5, damage_multiplier: 1.3, attack_cooldown: 1.2, new_attack_damage: 55, phase_name: "Phase 2 - Fury".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 2800, max_hp: 2800, speed: 55.0,
            state: EntityState::Idle, facing: 0.0, damage: 45,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(300.0, 500.0),
            attack_timer: 0.0, attack_duration: 0.7, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 350.0,
            boss_type: BossType::ChampionGundyr, name: "英雄古达".into(),
            boss_activated: false, current_attack: BossAttack::HalberdOverhead,
            attack_hit_range: 55.0, attack_index: 0,
        }
    }

    pub fn new_nameless_king(id: EntityId, x: f32, y: f32) -> Self {
        let phases = vec![
            BossPhase { health_threshold: 1.0, speed_multiplier: 1.0, damage_multiplier: 1.0, attack_cooldown: 2.0, new_attack_damage: 55, phase_name: "风暴之王".into() },
            BossPhase { health_threshold: 0.5, speed_multiplier: 1.3, damage_multiplier: 1.4, attack_cooldown: 1.3, new_attack_damage: 70, phase_name: "剑神降临".into() },
        ];
        Self {
            id, transform: Transform::new(x, y), hp: 2500, max_hp: 2500, speed: 50.0,
            state: EntityState::Idle, facing: 0.0, damage: 55,
            boss_ctrl: BossController::new(phases), aggro: AggroTable::new(350.0, 600.0),
            attack_timer: 0.0, attack_duration: 0.8, stagger_timer: 0.0,
            has_hit_this_attack: false, last_hit_window: 0, flash_timer: 0.0,
            is_charging: false, charge_speed: 350.0,
            boss_type: BossType::NamelessKing, name: "无名王者".into(),
            boss_activated: false, current_attack: BossAttack::ThrustAttack,
            attack_hit_range: 60.0, attack_index: 0,
        }
    }

    pub fn update_ai(&mut self, target_x: f32, target_y: f32, dt: f32) {
        if self.is_dead() || !self.boss_activated {
            return;
        }

        self.aggro.check_detection(
            self.transform.x,
            self.transform.y,
            1,
            target_x,
            target_y,
        );

        if !self.aggro.has_target() {
            self.state = EntityState::Idle;
            return;
        }

        let dx = self.aggro.last_known_x - self.transform.x;
        let dy = self.aggro.last_known_y - self.transform.y;
        let dist = (dx * dx + dy * dy).sqrt();
        self.facing = dy.atan2(dx);

        let hp_ratio = self.hp as f32 / self.max_hp as f32;
        let directive = self.boss_ctrl.update(hp_ratio, dt);

        let phase = self.boss_ctrl.current_phase();
        self.damage = (phase.new_attack_damage as f32 * phase.damage_multiplier) as i32;
        let speed_multiplier = phase.speed_multiplier;

        // Tick attack timer first
        if self.attack_timer > 0.0 {
            if self.is_charging {
                let charge_mult = match self.current_attack {
                    BossAttack::ShoulderCharge => 2.5,
                    BossAttack::IceMaceCharge => 1.8,
                    BossAttack::LeapingSlam => 3.0,
                    BossAttack::BodySlam => 2.0,
                    BossAttack::ChargeAttack => 2.5,
                    BossAttack::ThrustAttack => 2.0,
                    _ => 0.0, // Non-charging attacks don't move
                };
                let speed = self.charge_speed * charge_mult * dt;
                self.transform.x += self.facing.cos() * speed;
                self.transform.y += self.facing.sin() * speed;
            }
            self.attack_timer -= dt;
            if self.attack_timer <= 0.0 {
                self.is_charging = false;
                self.has_hit_this_attack = false;
                self.last_hit_window = 0;
                self.state = EntityState::Idle;
            }
            // While attacking, don't do other movement
            if self.flash_timer > 0.0 { self.flash_timer -= dt; }
            if self.stagger_timer > 0.0 { self.stagger_timer -= dt; }
            return;
        }

        // Staggered — don't move
        if self.stagger_timer > 0.0 {
            self.stagger_timer -= dt;
            self.state = EntityState::Staggered;
            if self.flash_timer > 0.0 { self.flash_timer -= dt; }
            return;
        }

        match directive {
            BossDirective::Chase => {
                let attack_range = self.attack_hit_range;
                let orbit_range = attack_range + 80.0;
                let approach_speed = self.speed * speed_multiplier * 0.6 * dt;
                let base_speed = self.speed * speed_multiplier * dt;

                if dist > orbit_range * 2.0 {
                    // Far away — approach directly but slowly
                    self.transform.x += self.facing.cos() * approach_speed;
                    self.transform.y += self.facing.sin() * approach_speed;
                    self.state = EntityState::Moving;
                } else if dist > orbit_range {
                    // Medium-far — approach with slight lateral drift
                    self.transform.x += self.facing.cos() * base_speed * 0.8;
                    self.transform.y += self.facing.sin() * base_speed * 0.8;
                    // Slight perpendicular drift
                    let perp = self.facing + std::f32::consts::FRAC_PI_2;
                    let drift = ((self.transform.x * 0.03 + self.transform.y * 0.07).sin()) * base_speed * 0.3;
                    self.transform.x += perp.cos() * drift;
                    self.transform.y += perp.sin() * drift;
                    self.state = EntityState::Moving;
                } else if dist > attack_range {
                    // Orbit range — circle around player instead of beelining
                    let perp = self.facing + std::f32::consts::FRAC_PI_2;
                    // Orbit direction changes periodically
                    let orbit_dir = if ((self.transform.x * 3.0 + self.transform.y * 7.0) as i32 / 50) % 2 == 0 { 1.0 } else { -1.0 };
                    let orbit_speed = base_speed * 0.7;
                    self.transform.x += perp.cos() * orbit_speed * orbit_dir;
                    self.transform.y += perp.sin() * orbit_speed * orbit_dir;
                    // Slowly close distance
                    self.transform.x += self.facing.cos() * base_speed * 0.2;
                    self.transform.y += self.facing.sin() * base_speed * 0.2;
                    self.state = EntityState::Moving;
                } else {
                    // In attack range — hold position, slight jitter
                    let jitter_x = (self.transform.x * 0.1).sin() * base_speed * 0.15;
                    let jitter_y = (self.transform.y * 0.1).cos() * base_speed * 0.15;
                    self.transform.x += jitter_x;
                    self.transform.y += jitter_y;
                    self.state = EntityState::Idle;
                }

                self.transform.scale_x = if dx < 0.0 { -1.0 } else { 1.0 };
            }
            BossDirective::Attack => {
                if self.attack_timer <= 0.0 {
                    self.state = EntityState::Attacking;
                    self.has_hit_this_attack = false;
                    self.last_hit_window = 0;

                    let attack = self.choose_attack(dist);

                    self.current_attack = attack;
                    self.is_charging = false;

                    match attack {
                        BossAttack::HalberdOverhead => {
                            self.attack_timer = 1.0;
                            self.attack_duration = 1.0;
                            self.attack_hit_range = 80.0;
                        }
                        BossAttack::ShoulderCharge => {
                            self.attack_timer = 0.5;
                            self.attack_duration = 0.5;
                            self.attack_hit_range = 50.0;
                            self.is_charging = true;
                        }
                        BossAttack::HalberdSweep => {
                            self.attack_timer = 0.8;
                            self.attack_duration = 0.8;
                            self.attack_hit_range = 100.0;
                        }
                        BossAttack::IceMaceCharge => {
                            self.attack_timer = 0.7;
                            self.attack_duration = 0.7;
                            self.attack_hit_range = 70.0;
                            self.is_charging = true;
                        }
                        BossAttack::IceBreadth => {
                            self.attack_timer = 1.2;
                            self.attack_duration = 1.2;
                            self.attack_hit_range = 90.0;
                        }
                        BossAttack::LeapingSlam => {
                            self.attack_timer = 1.4;
                            self.attack_duration = 1.4;
                            self.attack_hit_range = 120.0;
                            self.is_charging = true;
                        }
                        BossAttack::GroundSlam => {
                            self.attack_timer = 1.0;
                            self.attack_duration = 1.0;
                            self.attack_hit_range = 100.0;
                        }
                        BossAttack::SweepAttack => {
                            self.attack_timer = 0.7;
                            self.attack_duration = 0.7;
                            self.attack_hit_range = 90.0;
                        }
                        BossAttack::BodySlam => {
                            self.attack_timer = 1.2;
                            self.attack_duration = 1.2;
                            self.attack_hit_range = 80.0;
                            self.is_charging = true;
                        }
                        BossAttack::FlameBurst => {
                            self.attack_timer = 0.8;
                            self.attack_duration = 0.8;
                            self.attack_hit_range = 150.0;
                        }
                        BossAttack::ChargeAttack => {
                            self.attack_timer = 0.6;
                            self.attack_duration = 0.6;
                            self.attack_hit_range = 60.0;
                            self.is_charging = true;
                        }
                        BossAttack::HolyGround => {
                            self.attack_timer = 1.5;
                            self.attack_duration = 1.5;
                            self.attack_hit_range = 110.0;
                            self.is_charging = false;
                        }
                        BossAttack::ComboSlash => {
                            self.attack_timer = 0.5;
                            self.attack_duration = 0.5;
                            self.attack_hit_range = 70.0;
                        }
                        BossAttack::ThrustAttack => {
                            self.attack_timer = 0.8;
                            self.attack_duration = 0.8;
                            self.attack_hit_range = 120.0;
                            self.is_charging = true;
                        }
                        BossAttack::ShadowClone => {
                            self.attack_timer = 1.0;
                            self.attack_duration = 1.0;
                            self.attack_hit_range = 80.0;
                        }
                    }
                }
            }
            BossDirective::PhaseTransition => {
                self.state = EntityState::Idle;
            }
        }

        if self.flash_timer > 0.0 { self.flash_timer -= dt; }
        if self.stagger_timer > 0.0 { self.stagger_timer -= dt; }
    }

    pub fn is_phase_transitioning(&self) -> bool {
        self.boss_ctrl.is_transitioning
    }
}

impl Entity for Boss {
    fn id(&self) -> EntityId {
        self.id
    }
    fn position(&self) -> (f32, f32) {
        (self.transform.x, self.transform.y)
    }
    fn set_position(&mut self, x: f32, y: f32) {
        self.transform.x = x;
        self.transform.y = y;
    }
    fn hp(&self) -> i32 {
        self.hp
    }
    fn max_hp(&self) -> i32 {
        self.max_hp
    }
    fn state(&self) -> &EntityState {
        &self.state
    }

    fn update(&mut self, _dt: f32) {}

    fn render(&self, batcher: &mut SpriteBatcher, texture: &Texture, gl: &GL) {
        let phase_idx = self.boss_ctrl.current_phase_index();
        let (base_size, idle_color, move_color) = match self.boss_type {
            BossType::Vordt => (50.0, [0.4f32,0.5,0.7], [0.5f32,0.6,0.8]),
            BossType::IudexGundyr => (46.0, [0.6f32,0.6,0.5], [0.7f32,0.7,0.6]),
            BossType::Dancer => (42.0, [0.6f32,0.4,0.6], [0.7f32,0.5,0.7]),
            BossType::CurseRottedGreatwood => (48.0, [0.8f32,0.2,0.8], [0.9f32,0.3,0.9]),
            BossType::CrystalSage => (38.0, [0.4f32,0.6,0.9], [0.5f32,0.7,1.0]),
            BossType::AbyssWatchers => (44.0, [0.5f32,0.4,0.3], [0.6f32,0.5,0.4]),
            BossType::HighLordWolnir => (58.0, [0.3f32,0.2,0.4], [0.4f32,0.3,0.5]),
            BossType::OldDemonKing => (54.0, [0.7f32,0.3,0.1], [0.8f32,0.4,0.2]),
            BossType::DeaconsOfTheDeep => (52.0, [0.8f32,0.4,0.1], [0.9f32,0.5,0.2]),
            BossType::PontiffSulyvahn => (44.0, [0.3f32,0.5,0.8], [0.4f32,0.6,0.9]),
            BossType::Yhorm => (60.0, [0.5f32,0.4,0.3], [0.6f32,0.5,0.4]),
            BossType::Aldrich => (46.0, [0.5f32,0.2,0.6], [0.6f32,0.3,0.7]),
            BossType::DragonslayerArmour => (50.0, [0.6f32,0.6,0.5], [0.7f32,0.7,0.6]),
            BossType::TwinPrinces => (48.0, [0.6f32,0.5,0.7], [0.7f32,0.6,0.8]),
            BossType::SoulOfCinder => (46.0, [0.8f32,0.6,0.2], [0.9f32,0.7,0.3]),
            BossType::Oceiros => (52.0, [0.4f32,0.6,0.5], [0.5f32,0.7,0.6]),
            BossType::ChampionGundyr => (46.0, [0.5f32,0.5,0.4], [0.6f32,0.6,0.5]),
            BossType::NamelessKing => (48.0, [0.7f32,0.6,0.2], [0.8f32,0.7,0.3]),
        };
        let size = base_size + phase_idx as f32 * 6.0;

        if self.flash_timer > 0.0 {
            let instance = self.transform.to_instance_data(size, size, [0.0, 0.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0]);
            batcher.draw(instance, texture, gl);
            return;
        }

        let color = match self.state {
            EntityState::Idle => match phase_idx {
                0 => [idle_color[0], idle_color[1], idle_color[2], 1.0],
                1 => [idle_color[0] + 0.1, idle_color[1] - 0.1, idle_color[2] - 0.2, 1.0],
                _ => [1.0, 0.0, 0.3, 1.0],
            },
            EntityState::Moving => [move_color[0], move_color[1], move_color[2], 1.0],
            EntityState::Attacking => [idle_color[0], idle_color[1], idle_color[2], 1.0],
            EntityState::Staggered => [1.0, 1.0, 0.0, 1.0],
            EntityState::Dead => [0.2, 0.2, 0.2, 0.3],
            _ => [idle_color[0], idle_color[1], idle_color[2], 1.0],
        };

        // Attack animation progress (0.0 = start, 1.0 = end)
        let t = if self.attack_duration > 0.0 {
            1.0 - (self.attack_timer / self.attack_duration).max(0.0).min(1.0)
        } else {
            0.0
        };

        let dir_x = self.facing.cos();
        let dir_y = self.facing.sin();
        let side_x = -dir_y;
        let side_y = dir_x;

        // Boss identity silhouettes: weapon/limb layers stay visible even outside active hit frames.
        match self.boss_type {
            BossType::IudexGundyr => {
                let carry = if self.state == EntityState::Attacking { -0.12 } else { -0.65 };
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 20.0 + side_x * 10.0, self.transform.y + dir_y * 20.0 + side_y * 10.0, size * 1.55, size * 0.10, self.facing + carry, [0.62, 0.58, 0.48, 0.95]);
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 58.0 + side_x * 14.0, self.transform.y + dir_y * 58.0 + side_y * 14.0, size * 0.42, size * 0.24, self.facing + carry, [0.78, 0.76, 0.66, 0.95]);
                if phase_idx > 0 {
                    for i in 0..5 { let a = self.facing + (i as f32 - 2.0) * 0.55; draw_rect(batcher, texture, gl, self.transform.x - dir_x * 4.0 + a.cos() * (size * 0.55), self.transform.y - dir_y * 4.0 + a.sin() * (size * 0.55), size * 0.62, size * 0.12, a, [0.06, 0.02, 0.08, 0.55]); }
                }
            }
            BossType::ChampionGundyr => {
                let carry = if self.state == EntityState::Attacking { -0.08 } else { -0.55 };
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 18.0 + side_x * 8.0, self.transform.y + dir_y * 18.0 + side_y * 8.0, size * 1.45, size * 0.09, self.facing + carry, [0.55, 0.52, 0.42, 0.92]);
                if phase_idx > 0 {
                    draw_rect(batcher, texture, gl, self.transform.x - dir_x * 6.0 + side_x * 12.0, self.transform.y - dir_y * 6.0 + side_y * 12.0, size * 0.28, size * 0.22, self.facing + 0.4, [0.7, 0.5, 0.3, 0.6]);
                    draw_rect(batcher, texture, gl, self.transform.x - dir_x * 6.0 - side_x * 12.0, self.transform.y - dir_y * 6.0 - side_y * 12.0, size * 0.28, size * 0.22, self.facing - 0.4, [0.7, 0.5, 0.3, 0.6]);
                }
            }
            BossType::Vordt => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 28.0, self.transform.y + dir_y * 28.0, size * 0.72, size * 0.45, self.facing, [0.45, 0.62, 0.92, 0.58]);
                for i in 0..3 { let back = 18.0 + i as f32 * 14.0; draw_rect(batcher, texture, gl, self.transform.x - dir_x * back + side_x * ((i as f32 - 1.0) * 9.0), self.transform.y - dir_y * back + side_y * ((i as f32 - 1.0) * 9.0), size * 0.55, size * 0.08, self.facing, [0.55, 0.85, 1.0, 0.22]); }
            }
            BossType::Dancer => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 24.0 + side_x * 15.0, self.transform.y + dir_y * 24.0 + side_y * 15.0, size * 1.15, size * 0.06, self.facing + 0.22, [0.65, 0.35, 0.55, 0.75]);
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 22.0 - side_x * 15.0, self.transform.y + dir_y * 22.0 - side_y * 15.0, size * 1.05, size * 0.06, self.facing - 0.22, [0.55, 0.30, 0.65, 0.75]);
                if phase_idx > 0 { draw_rect(batcher, texture, gl, self.transform.x, self.transform.y, size * 1.6, size * 0.04, self.facing, [0.8, 0.3, 0.6, 0.3]); }
            }
            BossType::CurseRottedGreatwood => {
                for (ox, oy, rot) in [(-22.0, -8.0, -0.25), (20.0, 6.0, 0.18), (-10.0, 22.0, 0.04)] {
                    draw_rect(batcher, texture, gl, self.transform.x + ox, self.transform.y + oy, size * 0.72, size * 0.12, self.facing + rot, [0.24, 0.10, 0.18, 0.72]);
                }
            }
            BossType::CrystalSage => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 32.0, self.transform.y + dir_y * 32.0, size * 0.95, size * 0.06, self.facing, [0.5, 0.7, 1.0, 0.7]);
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 56.0, self.transform.y + dir_y * 56.0, size * 0.22, size * 0.22, self.facing, [0.7, 0.85, 1.0, 0.8]);
            }
            BossType::AbyssWatchers => {
                let glow = if phase_idx > 0 { 0.85 } else { 0.55 };
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 26.0, self.transform.y + dir_y * 26.0, size * 1.1, size * 0.07, self.facing, [0.7, 0.4, 0.2, glow]);
                draw_rect(batcher, texture, gl, self.transform.x - dir_x * 12.0, self.transform.y - dir_y * 12.0, size * 0.3, size * 0.18, self.facing, [0.4, 0.3, 0.2, 0.5]);
            }
            BossType::HighLordWolnir => {
                for (ox, oy) in [(-28.0, -15.0), (0.0, -22.0), (28.0, -15.0)] {
                    draw_rect(batcher, texture, gl, self.transform.x + ox, self.transform.y + oy, size * 0.28, size * 0.55, 0.0, [0.4, 0.3, 0.55, 0.6]);
                }
                draw_rect(batcher, texture, gl, self.transform.x, self.transform.y - size * 0.4, size * 0.55, size * 0.15, 0.0, [0.8, 0.7, 0.4, 0.7]);
            }
            BossType::OldDemonKing => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 24.0, self.transform.y + dir_y * 24.0, size * 0.85, size * 0.35, self.facing, [0.65, 0.25, 0.08, 0.7]);
                draw_rect(batcher, texture, gl, self.transform.x - dir_x * 18.0 + side_x * 20.0, self.transform.y - dir_y * 18.0 + side_y * 20.0, size * 0.4, size * 0.12, self.facing + 0.5, [0.5, 0.15, 0.05, 0.6]);
                draw_rect(batcher, texture, gl, self.transform.x - dir_x * 18.0 - side_x * 20.0, self.transform.y - dir_y * 18.0 - side_y * 20.0, size * 0.4, size * 0.12, self.facing - 0.5, [0.5, 0.15, 0.05, 0.6]);
            }
            BossType::DeaconsOfTheDeep => {
                for (ox, oy) in [(-20.0, -12.0), (0.0, -18.0), (20.0, -10.0), (-12.0, 16.0), (14.0, 15.0)] {
                    draw_rect(batcher, texture, gl, self.transform.x + ox, self.transform.y + oy, size * 0.34, size * 0.46, 0.0, [0.62, 0.12, 0.08, 0.72]);
                }
            }
            BossType::PontiffSulyvahn => {
                let glow = if phase_idx > 0 { 0.82 } else { 0.55 };
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 28.0 + side_x * 13.0, self.transform.y + dir_y * 28.0 + side_y * 13.0, size * 1.05, size * 0.08, self.facing + 0.12, [0.45, 0.72, 1.0, glow]);
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 26.0 - side_x * 13.0, self.transform.y + dir_y * 26.0 - side_y * 13.0, size * 0.95, size * 0.08, self.facing - 0.16, [0.82, 0.38, 0.98, glow]);
            }
            BossType::Yhorm => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 30.0, self.transform.y + dir_y * 30.0, size * 1.4, size * 0.14, self.facing, [0.55, 0.45, 0.35, 0.85]);
                if phase_idx > 0 { draw_rect(batcher, texture, gl, self.transform.x - dir_x * 8.0, self.transform.y - dir_y * 8.0, size * 0.5, size * 0.5, self.facing, [0.8, 0.3, 0.1, 0.4]); }
            }
            BossType::Aldrich => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 24.0, self.transform.y + dir_y * 24.0, size * 0.9, size * 0.06, self.facing, [0.6, 0.3, 0.8, 0.7]);
                draw_rect(batcher, texture, gl, self.transform.x - dir_x * 10.0, self.transform.y - dir_y * 10.0, size * 0.65, size * 0.55, self.facing, [0.35, 0.15, 0.45, 0.45]);
            }
            BossType::DragonslayerArmour => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 22.0, self.transform.y + dir_y * 22.0, size * 1.0, size * 0.10, self.facing, [0.72, 0.72, 0.58, 0.85]);
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 10.0 - side_x * 18.0, self.transform.y + dir_y * 10.0 - side_y * 18.0, size * 0.35, size * 0.45, self.facing, [0.6, 0.6, 0.5, 0.6]);
                if phase_idx > 0 { draw_rect(batcher, texture, gl, self.transform.x + dir_x * 36.0, self.transform.y + dir_y * 36.0, size * 0.18, size * 0.25, self.facing, [0.9, 0.85, 0.4, 0.7]); }
            }
            BossType::TwinPrinces => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 24.0, self.transform.y + dir_y * 24.0, size * 1.2, size * 0.09, self.facing, [0.65, 0.5, 0.75, 0.8]);
                draw_rect(batcher, texture, gl, self.transform.x - dir_x * 8.0 + side_x * 4.0, self.transform.y - dir_y * 8.0 + side_y * 4.0, size * 0.25, size * 0.25, self.facing, [0.8, 0.7, 0.9, 0.6]);
                if phase_idx > 0 { draw_rect(batcher, texture, gl, self.transform.x + dir_x * 18.0, self.transform.y + dir_y * 18.0, size * 0.15, size * 0.6, self.facing, [0.5, 0.7, 1.0, 0.5]); }
            }
            BossType::SoulOfCinder => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 22.0, self.transform.y + dir_y * 22.0, size * 1.15, size * 0.08, self.facing, [0.9, 0.7, 0.3, 0.85]);
                if phase_idx > 0 { for i in 0..4 { let a = self.facing + (i as f32 - 1.5) * 0.4; draw_rect(batcher, texture, gl, self.transform.x + a.cos() * size * 0.4, self.transform.y + a.sin() * size * 0.4, size * 0.4, size * 0.08, a, [1.0, 0.6, 0.2, 0.5]); } }
                if phase_idx > 1 { draw_rect(batcher, texture, gl, self.transform.x, self.transform.y, size * 1.3, size * 0.05, self.facing, [1.0, 0.9, 0.5, 0.7]); }
            }
            BossType::Oceiros => {
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 20.0, self.transform.y + dir_y * 20.0, size * 0.8, size * 0.35, self.facing, [0.45, 0.65, 0.55, 0.65]);
                draw_rect(batcher, texture, gl, self.transform.x - dir_x * 16.0 + side_x * 22.0, self.transform.y - dir_y * 16.0 + side_y * 22.0, size * 0.5, size * 0.10, self.facing + 0.6, [0.55, 0.75, 0.65, 0.5]);
                draw_rect(batcher, texture, gl, self.transform.x - dir_x * 16.0 - side_x * 22.0, self.transform.y - dir_y * 16.0 - side_y * 22.0, size * 0.5, size * 0.10, self.facing - 0.6, [0.55, 0.75, 0.65, 0.5]);
                if phase_idx > 0 { draw_rect(batcher, texture, gl, self.transform.x, self.transform.y, size * 0.45, size * 0.45, self.facing, [0.5, 0.8, 0.7, 0.3]); }
            }
            BossType::NamelessKing => {
                let carry = if self.state == EntityState::Attacking { -0.1 } else { -0.5 };
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 22.0 + side_x * 10.0, self.transform.y + dir_y * 22.0 + side_y * 10.0, size * 1.6, size * 0.08, self.facing + carry, [0.75, 0.7, 0.3, 0.92]);
                draw_rect(batcher, texture, gl, self.transform.x + dir_x * 60.0, self.transform.y + dir_y * 60.0, size * 0.3, size * 0.3, self.facing + carry, [0.9, 0.85, 0.4, 0.95]);
                if phase_idx > 0 {
                    for i in 0..4 { let a = self.facing + (i as f32 - 1.5) * 0.5; draw_rect(batcher, texture, gl, self.transform.x + a.cos() * (size * 0.7), self.transform.y + a.sin() * (size * 0.7), size * 0.5, size * 0.08, a, [0.9, 0.8, 0.2, 0.4]); }
                }
            }
        }

        // Charge trail effect (behind boss)
        if self.is_charging && self.state == EntityState::Attacking {
            for i in 1..4 {
                let trail_dist = i as f32 * 18.0;
                let alpha = 0.4 - i as f32 * 0.1;
                batcher.draw(
                    Transform::new(
                        self.transform.x - self.facing.cos() * trail_dist,
                        self.transform.y - self.facing.sin() * trail_dist,
                    ).to_instance_data(size * 0.9, size * 0.9, [0.0, 0.0, 1.0, 1.0], [1.0, 0.4, 0.0, alpha]),
                    texture, gl,
                );
            }
        }

        let (sx, sy) = if self.state == EntityState::Attacking {
            match self.current_attack {
                BossAttack::HalberdOverhead => {
                    if t < 0.4 { (0.85, 1.2 + t) } else { (1.3, 0.7) }
                }
                BossAttack::ShoulderCharge => {
                    (0.8 + t * 0.5, 0.9 - t * 0.2)
                }
                BossAttack::HalberdSweep => {
                    if t < 0.3 { (1.2, 0.9) } else { (1.4, 0.8) }
                }
                BossAttack::IceMaceCharge => {
                    (0.9 + t * 0.4, 0.85)
                }
                BossAttack::IceBreadth => {
                    if t < 0.4 { (1.15, 1.15) } else { (0.9, 0.9) }
                }
                BossAttack::LeapingSlam => {
                    if t < 0.5 { (0.7, 0.6) } else { (1.5, 1.3) }
                }
                BossAttack::GroundSlam => {
                    if t < 0.4 { (0.9, 1.3) } else { (1.4, 0.7) }
                }
                BossAttack::SweepAttack => {
                    if t < 0.3 { (1.1, 0.9) } else { (1.3, 0.75) }
                }
                BossAttack::BodySlam => {
                    if t < 0.5 { (0.7, 0.7) } else { (1.4, 1.3) }
                }
                BossAttack::FlameBurst => {
                    if t < 0.5 { (1.1, 1.1) } else { (0.95, 0.95) }
                }
                BossAttack::ChargeAttack => {
                    (0.8 + t * 0.5, 0.9 - t * 0.15)
                }
                BossAttack::HolyGround => {
                    if t < 0.5 { (0.9, 1.2) } else { (1.3, 0.8) }
                }
                BossAttack::ComboSlash => {
                    if t < 0.3 { (1.2, 0.85) } else if t < 0.6 { (0.85, 1.0) } else { (1.2, 0.85) }
                }
                BossAttack::ThrustAttack => {
                    if t < 0.3 { (0.8, 1.1) } else { (1.4, 0.7) }
                }
                BossAttack::ShadowClone => {
                    if t < 0.5 { (1.0, 1.0) } else { (0.9, 0.9) }
                }
            }
        } else if self.state == EntityState::Moving {
            // Walking animation — slight bob
            let bob = (self.transform.x * 0.1 + self.transform.y * 0.1).sin() * 0.05;
            (1.0 + bob, 1.0 - bob)
        } else {
            (1.0, 1.0)
        };

        let (body_forward, body_side) = if self.state == EntityState::Attacking {
            match self.current_attack {
                BossAttack::HalberdOverhead => {
                    if t < 0.45 { (-7.0, 5.0) } else { (11.0, 0.0) }
                }
                BossAttack::ShoulderCharge | BossAttack::IceMaceCharge | BossAttack::ChargeAttack => (10.0, 0.0),
                BossAttack::HalberdSweep | BossAttack::SweepAttack => {
                    (3.0, if t < 0.5 { -5.0 } else { 5.0 })
                }
                BossAttack::IceBreadth | BossAttack::FlameBurst => (-3.0, 0.0),
                BossAttack::LeapingSlam => {
                    if t < 0.52 { (22.0 * t, 0.0) } else { (10.0, 0.0) }
                }
                BossAttack::GroundSlam | BossAttack::HolyGround => {
                    if t < 0.48 { (-5.0, 0.0) } else { (7.0, 0.0) }
                }
                BossAttack::BodySlam => {
                    if t < 0.48 { (-4.0, 0.0) } else { (18.0, 0.0) }
                }
                BossAttack::ComboSlash => {
                    let side = if t < 0.5 { -7.0 } else { 7.0 };
                    (3.0, side)
                }
                BossAttack::ThrustAttack => (12.0, 0.0),
                BossAttack::ShadowClone => (2.0, 0.0),
            }
        } else {
            (0.0, 0.0)
        };

        let final_sx = size * sx;
        let final_sy = size * sy;

        // Draw boss body
        let mut body_transform = Transform::new(
            self.transform.x + dir_x * body_forward + side_x * body_side,
            self.transform.y + dir_y * body_forward + side_y * body_side,
        );
        body_transform.rotation = 0.0;
        body_transform.scale_x = self.transform.scale_x.signum();
        let instance = body_transform.to_instance_data(final_sx, final_sy, [0.0, 0.0, 1.0, 1.0], color);
        batcher.draw(instance, texture, gl);

        // Attack VFX — drawn ON TOP of boss
        if self.state == EntityState::Attacking {
            let fx = self.transform.x + self.facing.cos() * size * 0.6;
            let fy = self.transform.y + self.facing.sin() * size * 0.6;

            match self.current_attack {
                // Halberd overhead — yellow slash arc
                BossAttack::HalberdOverhead => {
                    let shaft_center = if t < 0.45 { -28.0 } else { 54.0 };
                    let shaft_angle = if t < 0.45 { self.facing - 0.95 } else { self.facing + 0.08 };
                    draw_rect(
                        batcher, texture, gl,
                        self.transform.x + dir_x * shaft_center + side_x * 8.0,
                        self.transform.y + dir_y * shaft_center + side_y * 8.0,
                        size * 1.95, size * 0.11,
                        shaft_angle,
                        [0.88, 0.80, 0.56, 0.98],
                    );
                    if t > 0.35 {
                        let arc_alpha = if t < 0.6 { (t - 0.35) * 4.0 } else { 1.0 - (t - 0.6) * 2.5 };
                        draw_rect(
                            batcher, texture, gl,
                            fx + dir_x * 22.0, fy + dir_y * 22.0,
                            size * 1.72, size * 0.34,
                            self.facing + 0.08,
                            [1.0, 0.9, 0.2, arc_alpha.max(0.0).min(1.0)],
                        );
                    }
                }
                // Shoulder charge — red impact burst
                BossAttack::ShoulderCharge => {
                    if t > 0.3 {
                        let burst_alpha = (1.0 - t).max(0.0);
                        batcher.draw(
                            Transform::new(fx, fy).to_instance_data(
                                size * 0.8, size * 0.8, [0.0, 0.0, 1.0, 1.0],
                                [1.0, 0.3, 0.0, burst_alpha * 0.6]
                            ), texture, gl,
                        );
                    }
                }
                // Halberd sweep — wide horizontal arc
                BossAttack::HalberdSweep => {
                    if t > 0.25 {
                        let sweep_alpha = (1.0 - t).max(0.0);
                        for i in 0..4 {
                            let offset = (i as f32 - 1.5) * 18.0;
                            let reach = 32.0 + i as f32 * 12.0;
                            draw_rect(
                                batcher, texture, gl,
                                self.transform.x + dir_x * reach + side_x * offset,
                                self.transform.y + dir_y * reach + side_y * offset,
                                size * 0.58, size * 0.14,
                                self.facing,
                                [1.0, 0.7, 0.1, sweep_alpha * 0.42],
                            );
                        }
                    }
                }
                // Ice mace — blue impact
                BossAttack::IceMaceCharge => {
                    if t > 0.3 {
                        batcher.draw(
                            Transform::new(fx, fy).to_instance_data(
                                size * 0.9, size * 0.9, [0.0, 0.0, 1.0, 1.0],
                                [0.4, 0.7, 1.0, 0.5]
                            ), texture, gl,
                        );
                    }
                }
                // Ice breadth — cone spray
                BossAttack::IceBreadth => {
                    if t > 0.35 {
                        let breath_len = (t - 0.35) * 3.0;
                        for i in 0..7 {
                            let spread = (i as f32 - 3.0) * 0.16;
                            let lane = i as f32 - 3.0;
                            let bx = fx + dir_x * breath_len * 36.0 + side_x * lane * 10.0;
                            let by = fy + dir_y * breath_len * 36.0 + side_y * lane * 10.0;
                            draw_rect(
                                batcher, texture, gl,
                                bx, by,
                                size * (0.45 + breath_len * 0.5), size * 0.16,
                                self.facing + spread,
                                [0.58, 0.90, 1.0, (1.0 - t).max(0.0) * 0.58],
                            );
                        }
                    }
                }
                // Leaping slam — shadow on ground + impact ring
                BossAttack::LeapingSlam => {
                    if t < 0.5 {
                        // Shadow on ground (stays at landing point)
                        batcher.draw(
                            Transform::new(fx, fy).to_instance_data(
                                size * 0.5, size * 0.5, [0.0, 0.0, 1.0, 1.0],
                                [0.2, 0.2, 0.2, 0.4]
                            ), texture, gl,
                        );
                    } else {
                        // Impact ring expanding outward
                        let ring_t = (t - 0.5) * 2.0;
                        let ring_size = size * (0.5 + ring_t * 2.0);
                        batcher.draw(
                            Transform::new(self.transform.x, self.transform.y).to_instance_data(
                                ring_size, ring_size * 0.3, [0.0, 0.0, 1.0, 1.0],
                                [0.3, 0.5, 1.0, (1.0 - ring_t) * 0.6]
                            ), texture, gl,
                        );
                    }
                }
                // Ground slam — purple AoE ring
                BossAttack::GroundSlam => {
                    if t > 0.35 {
                        let ring_t = (t - 0.35) * 1.5;
                        for i in 0..8 {
                            let a = i as f32 * std::f32::consts::TAU / 8.0;
                            draw_rect(
                                batcher, texture, gl,
                                self.transform.x + a.cos() * size * ring_t,
                                self.transform.y + a.sin() * size * ring_t,
                                size * 0.8, size * 0.12,
                                a,
                                [0.35, 0.13, 0.20, (1.0 - ring_t).max(0.0) * 0.55],
                            );
                        }
                        batcher.draw(
                            Transform::new(self.transform.x, self.transform.y).to_instance_data(
                                size * (0.3 + ring_t * 2.5), size * (0.3 + ring_t * 2.5), [0.0, 0.0, 1.0, 1.0],
                                [0.8, 0.2, 0.8, (1.0 - ring_t) * 0.5]
                            ), texture, gl,
                        );
                    }
                }
                // Sweep attack — wide arc
                BossAttack::SweepAttack => {
                    if t > 0.25 {
                        batcher.draw(
                            Transform::new(self.transform.x, self.transform.y).to_instance_data(
                                size * 1.8, size * 0.3, [0.0, 0.0, 1.0, 1.0],
                                [0.7, 0.15, 0.7, (1.0 - t) * 0.6]
                            ), texture, gl,
                        );
                    }
                }
                // Body slam — expanding impact
                BossAttack::BodySlam => {
                    if t > 0.45 {
                        let slam_t = (t - 0.45) * 1.8;
                        batcher.draw(
                            Transform::new(self.transform.x, self.transform.y).to_instance_data(
                                size * (0.5 + slam_t * 2.0), size * (0.5 + slam_t * 2.0), [0.0, 0.0, 1.0, 1.0],
                                [0.5, 0.1, 0.5, (1.0 - slam_t) * 0.5]
                            ), texture, gl,
                        );
                    }
                }
                // Flame burst — fireball
                BossAttack::FlameBurst => {
                    if t > 0.4 {
                        let flame_t = (t - 0.4) * 1.6;
                        let flame_x = self.transform.x + self.facing.cos() * (30.0 + flame_t * 80.0);
                        let flame_y = self.transform.y + self.facing.sin() * (30.0 + flame_t * 80.0);
                        draw_rect(
                            batcher, texture, gl,
                            flame_x, flame_y,
                            size * 0.58 * (1.0 + flame_t), size * 0.58 * (1.0 + flame_t),
                            self.facing + flame_t,
                            [1.0, 0.36, 0.04, (1.0 - flame_t).max(0.0) * 0.85],
                        );
                        draw_rect(
                            batcher, texture, gl,
                            flame_x - dir_x * 18.0, flame_y - dir_y * 18.0,
                            size * 0.72, size * 0.12,
                            self.facing,
                            [1.0, 0.82, 0.18, (1.0 - flame_t).max(0.0) * 0.55],
                        );
                    }
                }
                // Charge attack — red streak
                BossAttack::ChargeAttack => {
                    if t > 0.2 {
                        batcher.draw(
                            Transform::new(fx, fy).to_instance_data(
                                size * 0.6, size * 0.6, [0.0, 0.0, 1.0, 1.0],
                                [1.0, 0.2, 0.0, 0.6]
                            ), texture, gl,
                        );
                    }
                }
                // Holy ground — golden ring expanding
                BossAttack::HolyGround => {
                    if t > 0.45 {
                        let ring_t = (t - 0.45) * 1.8;
                        for i in 0..10 {
                            let a = i as f32 * std::f32::consts::TAU / 10.0;
                            draw_rect(
                                batcher, texture, gl,
                                self.transform.x + a.cos() * size * (0.7 + ring_t),
                                self.transform.y + a.sin() * size * (0.7 + ring_t) * 0.42,
                                size * 0.14, size * 0.58,
                                a + std::f32::consts::FRAC_PI_2,
                                [1.0, 0.92, 0.42, (1.0 - ring_t).max(0.0) * 0.52],
                            );
                        }
                        batcher.draw(
                            Transform::new(self.transform.x, self.transform.y).to_instance_data(
                                size * (0.4 + ring_t * 2.5), size * (0.4 + ring_t * 2.5) * 0.4, [0.0, 0.0, 1.0, 1.0],
                                [1.0, 0.95, 0.3, (1.0 - ring_t) * 0.6]
                            ), texture, gl,
                        );
                    }
                }
                // Combo slash — two quick slashes
                BossAttack::ComboSlash => {
                    let slash_count = if t > 0.5 { 2 } else { 1 };
                    for s in 0..slash_count {
                        let st = if s == 0 { (t * 2.0).min(1.0) } else { ((t - 0.5) * 2.0).min(1.0) };
                        let offset = (s as f32 - 0.5) * 15.0;
                        draw_rect(
                            batcher, texture, gl,
                            fx + side_x * offset + dir_x * size * st * 0.4,
                            fy + side_y * offset + dir_y * size * st * 0.4,
                            size * 1.28 * st, size * 0.18,
                            self.facing + if s == 0 { -0.58 } else { 0.58 },
                            if s == 0 { [0.5, 0.7, 1.0, (1.0 - st) * 0.78] } else { [0.88, 0.35, 1.0, (1.0 - st) * 0.72] },
                        );
                    }
                }
                // Thrust — long narrow line forward
                BossAttack::ThrustAttack => {
                    if t > 0.25 {
                        let thrust_len = (t - 0.25) * 2.0;
                        batcher.draw(
                            Transform::new(
                                self.transform.x + self.facing.cos() * size * thrust_len,
                                self.transform.y + self.facing.sin() * size * thrust_len,
                            ).to_instance_data(
                                size * 1.5 * thrust_len, size * 0.15, [0.0, 0.0, 1.0, 1.0],
                                [0.4, 0.5, 1.0, (1.0 - t) * 0.7]
                            ), texture, gl,
                        );
                    }
                }
                // Shadow clone — ghost duplicate
                BossAttack::ShadowClone => {
                    if t > 0.4 {
                        let ghost_offset = size * 0.8;
                        let ghost_x = self.transform.x - side_x * ghost_offset * 0.85 + dir_x * ghost_offset;
                        let ghost_y = self.transform.y - side_y * ghost_offset * 0.85 + dir_y * ghost_offset;
                        batcher.draw(
                            Transform::new(ghost_x, ghost_y).to_instance_data(
                                size, size, [0.0, 0.0, 1.0, 1.0],
                                [idle_color[0], idle_color[1], idle_color[2], 0.35]
                            ), texture, gl,
                        );
                        draw_rect(
                            batcher, texture, gl,
                            ghost_x + dir_x * 30.0,
                            ghost_y + dir_y * 30.0,
                            size * 1.08, size * 0.08,
                            self.facing + 0.32,
                            [0.55, 0.65, 1.0, 0.42],
                        );
                    }
                }
            }
        }
    }

    fn take_damage(&mut self, info: &DamageInfo) -> DamageOutcome {
        if self.boss_ctrl.is_transitioning {
            return DamageOutcome::ignored(info.damage);
        }
        self.hp -= info.damage;
        self.flash_timer = 0.12;
        self.stagger_timer = 0.2;
        let killed = self.hp <= 0;
        if killed {
            self.hp = 0;
            self.state = EntityState::Dead;
        }
        DamageOutcome::applied(info.damage, info.damage, killed)
    }

    fn is_dead(&self) -> bool {
        self.hp <= 0
    }
}

fn in_front(forward: f32, side: f32, min_forward: f32, max_forward: f32, half_width: f32) -> bool {
    forward >= min_forward && forward <= max_forward && side.abs() <= half_width
}

fn draw_rect(
    batcher: &mut SpriteBatcher,
    texture: &Texture,
    gl: &GL,
    x: f32,
    y: f32,
    w: f32,
    h: f32,
    rotation: f32,
    color: [f32; 4],
) {
    let mut transform = Transform::new(x, y);
    transform.rotation = rotation;
    batcher.draw(transform.to_instance_data(w, h, [0.0, 0.0, 1.0, 1.0], color), texture, gl);
}
