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

        self.damage = self.boss_ctrl.current_phase().new_attack_damage;
        let speed_multiplier = self.boss_ctrl.current_phase().speed_multiplier;

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

                    let attack = match self.boss_type {
                        BossType::IudexGundyr => {
                            match self.attack_index % 3 {
                                0 => BossAttack::HalberdOverhead,
                                1 => BossAttack::ShoulderCharge,
                                _ => BossAttack::HalberdSweep,
                            }
                        }
                        BossType::Vordt => {
                            match self.attack_index % 3 {
                                0 => BossAttack::IceMaceCharge,
                                1 => BossAttack::IceBreadth,
                                _ => BossAttack::LeapingSlam,
                            }
                        }
                        BossType::DemonKnight => {
                            match self.attack_index % 3 {
                                0 => BossAttack::GroundSlam,
                                1 => BossAttack::SweepAttack,
                                _ => BossAttack::BodySlam,
                            }
                        }
                        BossType::Dragonrider => {
                            match self.attack_index % 3 {
                                0 => BossAttack::FlameBurst,
                                1 => BossAttack::ChargeAttack,
                                _ => BossAttack::HolyGround,
                            }
                        }
                        BossType::RuinSentinel => {
                            match self.attack_index % 3 {
                                0 => BossAttack::ComboSlash,
                                1 => BossAttack::ThrustAttack,
                                _ => BossAttack::ShadowClone,
                            }
                        }
                    };
                    self.attack_index += 1;

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
                        BossAttack::HolyGround => {
                            self.attack_timer = 1.5;
                            self.attack_duration = 1.5;
                            self.attack_hit_range = 110.0;
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

        // Squash/stretch
        let (sx, sy) = if self.state == EntityState::Attacking {
            match self.current_attack {
                // Overhead: windup = stretch tall, hit = squash wide
                BossAttack::HalberdOverhead => {
                    if t < 0.4 { (0.85, 1.2 + t) } else { (1.3, 0.7) }
                }
                // Shoulder charge: lean forward, compress
                BossAttack::ShoulderCharge => {
                    (0.8 + t * 0.5, 0.9 - t * 0.2)
                }
                // Sweep: wide stretch horizontally
                BossAttack::HalberdSweep => {
                    if t < 0.3 { (1.2, 0.9) } else { (1.4, 0.8) }
                }
                // Ice mace: forward lean
                BossAttack::IceMaceCharge => {
                    (0.9 + t * 0.4, 0.85)
                }
                // Ice breadth: puff up then release
                BossAttack::IceBreadth => {
                    if t < 0.4 { (1.15, 1.15) } else { (0.9, 0.9) }
                }
                // Leap: jump up (shrink) then slam down (wide)
                BossAttack::LeapingSlam => {
                    if t < 0.5 { (0.7, 0.6) } else { (1.5, 1.3) }
                }
                // Ground slam: raise then smash
                BossAttack::GroundSlam => {
                    if t < 0.4 { (0.9, 1.3) } else { (1.4, 0.7) }
                }
                // Sweep: wide
                BossAttack::SweepAttack => {
                    if t < 0.3 { (1.1, 0.9) } else { (1.3, 0.75) }
                }
                // Body slam: shrink then expand
                BossAttack::BodySlam => {
                    if t < 0.5 { (0.7, 0.7) } else { (1.4, 1.3) }
                }
                // Flame: puff up
                BossAttack::FlameBurst => {
                    if t < 0.5 { (1.1, 1.1) } else { (0.95, 0.95) }
                }
                // Charge: lean
                BossAttack::ChargeAttack => {
                    (0.8 + t * 0.5, 0.9 - t * 0.15)
                }
                // Holy ground: float up then slam
                BossAttack::HolyGround => {
                    if t < 0.5 { (0.9, 1.2) } else { (1.3, 0.8) }
                }
                // Combo: quick stretches
                BossAttack::ComboSlash => {
                    if t < 0.3 { (1.2, 0.85) } else if t < 0.6 { (0.85, 1.0) } else { (1.2, 0.85) }
                }
                // Thrust: elongate forward
                BossAttack::ThrustAttack => {
                    if t < 0.3 { (0.8, 1.1) } else { (1.4, 0.7) }
                }
                // Shadow clone: split effect
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

        let final_sx = size * sx;
        let final_sy = size * sy;

        // Draw boss body
        let instance = self.transform.to_instance_data(final_sx, final_sy, [0.0, 0.0, 1.0, 1.0], color);
        batcher.draw(instance, texture, gl);

        // Attack VFX — drawn ON TOP of boss
        if self.state == EntityState::Attacking {
            let fx = self.transform.x + self.facing.cos() * size * 0.6;
            let fy = self.transform.y + self.facing.sin() * size * 0.6;

            match self.current_attack {
                // Halberd overhead — yellow slash arc
                BossAttack::HalberdOverhead => {
                    if t > 0.35 {
                        let arc_alpha = if t < 0.6 { (t - 0.35) * 4.0 } else { 1.0 - (t - 0.6) * 2.5 };
                        batcher.draw(
                            Transform::new(fx, fy).to_instance_data(
                                size * 1.6, size * 0.4, [0.0, 0.0, 1.0, 1.0],
                                [1.0, 0.9, 0.2, arc_alpha.max(0.0).min(1.0)]
                            ), texture, gl,
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
                        batcher.draw(
                            Transform::new(self.transform.x, self.transform.y).to_instance_data(
                                size * 2.0, size * 0.3, [0.0, 0.0, 1.0, 1.0],
                                [1.0, 0.7, 0.1, sweep_alpha * 0.7]
                            ), texture, gl,
                        );
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
                        for i in 0..3 {
                            let offset = (i as f32 - 1.0) * 12.0;
                            let bx = fx + self.facing.cos() * breath_len * 20.0;
                            let by = fy + self.facing.sin() * breath_len * 20.0 + offset;
                            batcher.draw(
                                Transform::new(bx, by).to_instance_data(
                                    size * 0.6 * breath_len, size * 0.25, [0.0, 0.0, 1.0, 1.0],
                                    [0.6, 0.9, 1.0, (1.0 - t) * 0.5]
                                ), texture, gl,
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
                        batcher.draw(
                            Transform::new(flame_x, flame_y).to_instance_data(
                                size * 0.5 * (1.0 + flame_t), size * 0.5 * (1.0 + flame_t), [0.0, 0.0, 1.0, 1.0],
                                [1.0, 0.5, 0.0, (1.0 - flame_t) * 0.8]
                            ), texture, gl,
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
                        batcher.draw(
                            Transform::new(fx + offset, fy + offset).to_instance_data(
                                size * 1.2 * st, size * 0.2, [0.0, 0.0, 1.0, 1.0],
                                [0.5, 0.7, 1.0, (1.0 - st) * 0.7]
                            ), texture, gl,
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
                        let ghost_x = self.transform.x + self.facing.cos() * ghost_offset;
                        let ghost_y = self.transform.y + self.facing.sin() * ghost_offset;
                        batcher.draw(
                            Transform::new(ghost_x, ghost_y).to_instance_data(
                                size, size, [0.0, 0.0, 1.0, 1.0],
                                [idle_color[0], idle_color[1], idle_color[2], 0.35]
                            ), texture, gl,
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
