use crate::ai::aggro::AggroTable;
use crate::ai::boss_ai::{BossController, BossDirective, BossPhase};
use crate::core::transform::Transform;
use crate::entity::entity_trait::{DamageInfo, Entity, EntityId, EntityState};
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use web_sys::WebGl2RenderingContext as GL;

#[derive(Clone, Copy, PartialEq)]
pub enum BossType {
    DemonKnight,
    Dragonrider,
    RuinSentinel,
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
            hp: 800,
            max_hp: 800,
            speed: 40.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 50,
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
            name: "DEMON KNIGHT".into(),
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
            hp: 1000,
            max_hp: 1000,
            speed: 55.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 40,
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
            name: "DRAGONRIDER".into(),
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
            hp: 600,
            max_hp: 600,
            speed: 50.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 35,
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
            name: "RUIN SENTINEL".into(),
        }
    }

    pub fn update_ai(&mut self, target_x: f32, target_y: f32, dt: f32) {
        if self.is_dead() {
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

        // Face target
        let dx = self.aggro.last_known_x - self.transform.x;
        let dy = self.aggro.last_known_y - self.transform.y;
        self.facing = dy.atan2(dx);

        let hp_ratio = self.hp as f32 / self.max_hp as f32;
        let directive = self.boss_ctrl.update(hp_ratio, dt);

        self.damage = self.boss_ctrl.current_phase().new_attack_damage;
        let speed_multiplier = self.boss_ctrl.current_phase().speed_multiplier;

        match directive {
            BossDirective::Chase => {
                let speed = self.speed * speed_multiplier * dt;
                self.transform.x += self.facing.cos() * speed;
                self.transform.y += self.facing.sin() * speed;
                self.transform.scale_x = if self.facing.cos() < 0.0 { -1.0 } else { 1.0 };
                self.state = EntityState::Moving;
            }
            BossDirective::Attack => {
                if self.attack_timer <= 0.0 {
                    self.state = EntityState::Attacking;
                    self.attack_timer = self.attack_duration;
                    self.has_hit_this_attack = false;
                    self.is_charging = true;
                }
            }
            BossDirective::PhaseTransition => {
                self.state = EntityState::Idle; // Invulnerable during transition
            }
        }

        // Tick attack timer — charge toward player while attacking
        if self.attack_timer > 0.0 {
            if self.is_charging {
                let speed = self.charge_speed * dt;
                self.transform.x += self.facing.cos() * speed;
                self.transform.y += self.facing.sin() * speed;
            }
            self.attack_timer -= dt;
            if self.attack_timer <= 0.0 {
                self.is_charging = false;
                self.state = EntityState::Moving;
            }
        }
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
            EntityState::Attacking => {
                if self.is_charging {
                    [1.0, 0.5, 0.0, 1.0]
                } else {
                    [1.0, 0.0, 0.0, 1.0]
                }
            }
            EntityState::Staggered => [1.0, 1.0, 0.0, 1.0],
            EntityState::Dead => [0.2, 0.2, 0.2, 0.3],
            _ => [idle_color[0], idle_color[1], idle_color[2], 1.0],
        };

        // Charge trail effect
        if self.is_charging {
            batcher.draw(
                self.transform.to_instance_data(size * 0.8, size * 0.8, [0.0, 0.0, 1.0, 1.0], [1.0, 0.3, 0.0, 0.3]),
                texture, gl,
            );
        }

        let instance = self.transform.to_instance_data(size, size, [0.0, 0.0, 1.0, 1.0], color);
        batcher.draw(instance, texture, gl);
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
