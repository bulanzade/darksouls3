use crate::ai::aggro::AggroTable;
use crate::ai::boss_ai::{BossController, BossDirective, BossPhase};
use crate::core::transform::Transform;
use crate::entity::entity_trait::{DamageInfo, Entity, EntityId, EntityState};
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use web_sys::WebGl2RenderingContext as GL;

#[derive(Clone, Copy, PartialEq)]
pub enum BossType {
    IudexGundyr,
    Vordt,
    DemonKnight,
    Dragonrider,
    RuinSentinel,
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
    // DemonKnight (Curse-rotted Greatwood)
    GroundSlam,         // 砸地 — stomp with AoE
    SweepAttack,        // 横扫 — wide arm sweep
    BodySlam,           // 倒压 — fall forward onto player
    // Dragonrider (Deacons)
    FlameBurst,         // 火焰爆发 — ranged fireball
    ChargeAttack,       // 冲锋攻击 — lance charge
    HolyGround,         // 圣光地面 — AoE burst at feet
    // RuinSentinel (Pontiff)
    ComboSlash,         // 连斩 — 2-hit combo
    ThrustAttack,       // 突刺 — long range thrust
    ShadowClone,        // 影分身 — spawn a ghost that mimics next attack
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
        if self.state != EntityState::Attacking || self.has_hit_this_attack {
            return false;
        }

        let t = self.attack_progress();
        if !self.attack_active_at(t) {
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

    fn attack_active_at(&self, t: f32) -> bool {
        match self.current_attack {
            BossAttack::HalberdOverhead => (0.44..=0.68).contains(&t),
            BossAttack::ShoulderCharge => (0.16..=0.88).contains(&t),
            BossAttack::HalberdSweep => (0.34..=0.78).contains(&t),
            BossAttack::IceMaceCharge => (0.20..=0.90).contains(&t),
            BossAttack::IceBreadth => (0.38..=0.96).contains(&t),
            BossAttack::LeapingSlam => (0.54..=0.78).contains(&t),
            BossAttack::GroundSlam => (0.44..=0.70).contains(&t),
            BossAttack::SweepAttack => (0.30..=0.74).contains(&t),
            BossAttack::BodySlam => (0.52..=0.82).contains(&t),
            BossAttack::FlameBurst => (0.42..=0.76).contains(&t),
            BossAttack::ChargeAttack => (0.16..=0.88).contains(&t),
            BossAttack::HolyGround => (0.54..=0.78).contains(&t),
            BossAttack::ComboSlash => (0.18..=0.38).contains(&t) || (0.56..=0.80).contains(&t),
            BossAttack::ThrustAttack => (0.34..=0.72).contains(&t),
            BossAttack::ShadowClone => (0.54..=0.86).contains(&t),
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
            BossType::DemonKnight => {
                if dist > 105.0 {
                    BossAttack::BodySlam
                } else if phase > 1 || seq % 3 == 0 {
                    BossAttack::GroundSlam
                } else {
                    BossAttack::SweepAttack
                }
            }
            BossType::Dragonrider => {
                if dist > 125.0 {
                    BossAttack::FlameBurst
                } else if phase > 0 && seq % 2 == 0 {
                    BossAttack::HolyGround
                } else {
                    BossAttack::ChargeAttack
                }
            }
            BossType::RuinSentinel => {
                if phase > 0 && seq % 4 == 0 {
                    BossAttack::ShadowClone
                } else if dist > 86.0 {
                    BossAttack::ThrustAttack
                } else {
                    BossAttack::ComboSlash
                }
            }
        }
    }

    pub fn new_test_boss(id: EntityId, x: f32, y: f32) -> Self {
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
            flash_timer: 0.0,
            is_charging: false,
            charge_speed: 300.0,
            boss_type: BossType::DemonKnight,
            name: "咒蚀大树".into(),
            boss_activated: false,
            current_attack: BossAttack::GroundSlam,
            attack_hit_range: 48.0,
            attack_index: 0,
        }
    }

    pub fn new_dragonrider(id: EntityId, x: f32, y: f32) -> Self {
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
            flash_timer: 0.0,
            is_charging: false,
            charge_speed: 400.0,
            boss_type: BossType::Dragonrider,
            name: "幽邃主教群".into(),
            boss_activated: false,
            current_attack: BossAttack::GroundSlam,
            attack_hit_range: 48.0,
            attack_index: 0,
        }
    }

    pub fn new_ruin_sentinel(id: EntityId, x: f32, y: f32) -> Self {
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
            flash_timer: 0.0,
            is_charging: false,
            charge_speed: 350.0,
            boss_type: BossType::RuinSentinel,
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
                // Combat distances: approach range, orbit range, attack range
                let attack_range = match self.boss_type {
                    BossType::Vordt => 70.0,
                    BossType::IudexGundyr => 65.0,
                    BossType::DemonKnight => 80.0,
                    BossType::Dragonrider => 75.0,
                    BossType::RuinSentinel => 60.0,
                };
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
            BossType::DemonKnight => (48.0, [0.8f32,0.2,0.8], [0.9f32,0.3,0.9]),
            BossType::Dragonrider => (52.0, [0.8f32,0.4,0.1], [0.9f32,0.5,0.2]),
            BossType::RuinSentinel => (44.0, [0.3f32,0.5,0.8], [0.4f32,0.6,0.9]),
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
                draw_rect(
                    batcher, texture, gl,
                    self.transform.x + dir_x * 20.0 + side_x * 10.0,
                    self.transform.y + dir_y * 20.0 + side_y * 10.0,
                    size * 1.55, size * 0.10,
                    self.facing + carry,
                    [0.62, 0.58, 0.48, 0.95],
                );
                draw_rect(
                    batcher, texture, gl,
                    self.transform.x + dir_x * 58.0 + side_x * 14.0,
                    self.transform.y + dir_y * 58.0 + side_y * 14.0,
                    size * 0.42, size * 0.24,
                    self.facing + carry,
                    [0.78, 0.76, 0.66, 0.95],
                );
                if phase_idx > 0 {
                    for i in 0..5 {
                        let a = self.facing + (i as f32 - 2.0) * 0.55;
                        draw_rect(
                            batcher, texture, gl,
                            self.transform.x - dir_x * 4.0 + a.cos() * (size * 0.55),
                            self.transform.y - dir_y * 4.0 + a.sin() * (size * 0.55),
                            size * 0.62, size * 0.12,
                            a,
                            [0.06, 0.02, 0.08, 0.55],
                        );
                    }
                }
            }
            BossType::Vordt => {
                draw_rect(
                    batcher, texture, gl,
                    self.transform.x + dir_x * 28.0,
                    self.transform.y + dir_y * 28.0,
                    size * 0.72, size * 0.45,
                    self.facing,
                    [0.45, 0.62, 0.92, 0.58],
                );
                for i in 0..3 {
                    let back = 18.0 + i as f32 * 14.0;
                    draw_rect(
                        batcher, texture, gl,
                        self.transform.x - dir_x * back + side_x * ((i as f32 - 1.0) * 9.0),
                        self.transform.y - dir_y * back + side_y * ((i as f32 - 1.0) * 9.0),
                        size * 0.55, size * 0.08,
                        self.facing,
                        [0.55, 0.85, 1.0, 0.22],
                    );
                }
            }
            BossType::DemonKnight => {
                for (ox, oy, rot) in [(-22.0, -8.0, -0.25), (20.0, 6.0, 0.18), (-10.0, 22.0, 0.04)] {
                    draw_rect(
                        batcher, texture, gl,
                        self.transform.x + ox,
                        self.transform.y + oy,
                        size * 0.72, size * 0.12,
                        self.facing + rot,
                        [0.24, 0.10, 0.18, 0.72],
                    );
                }
            }
            BossType::Dragonrider => {
                for (ox, oy) in [(-20.0, -12.0), (0.0, -18.0), (20.0, -10.0), (-12.0, 16.0), (14.0, 15.0)] {
                    draw_rect(
                        batcher, texture, gl,
                        self.transform.x + ox,
                        self.transform.y + oy,
                        size * 0.34, size * 0.46,
                        0.0,
                        [0.62, 0.12, 0.08, 0.72],
                    );
                }
            }
            BossType::RuinSentinel => {
                let glow = if phase_idx > 0 { 0.82 } else { 0.55 };
                draw_rect(
                    batcher, texture, gl,
                    self.transform.x + dir_x * 28.0 + side_x * 13.0,
                    self.transform.y + dir_y * 28.0 + side_y * 13.0,
                    size * 1.05, size * 0.08,
                    self.facing + 0.12,
                    [0.45, 0.72, 1.0, glow],
                );
                draw_rect(
                    batcher, texture, gl,
                    self.transform.x + dir_x * 26.0 - side_x * 13.0,
                    self.transform.y + dir_y * 26.0 - side_y * 13.0,
                    size * 0.95, size * 0.08,
                    self.facing - 0.16,
                    [0.82, 0.38, 0.98, glow],
                );
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

    fn take_damage(&mut self, info: &DamageInfo) {
        if self.boss_ctrl.is_transitioning {
            return;
        } // Invulnerable during phase transition
        self.hp -= info.damage;
        self.flash_timer = 0.12;
        self.stagger_timer = 0.2;
        if self.hp <= 0 {
            self.hp = 0;
            self.state = EntityState::Dead;
        }
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
