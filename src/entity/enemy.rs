use crate::ai::aggro::AggroTable;
use crate::ai::state_machine::*;
use crate::core::transform::Transform;
use crate::entity::entity_trait::{DamageInfo, Entity, EntityId, EntityState};
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use web_sys::WebGl2RenderingContext as GL;

#[derive(Clone, Copy, PartialEq)]
pub enum EnemyKind {
    HollowSoldier,
    Archer,
    Knight,
    Assassin,
    DarkMage,
    Mimic,
}

pub struct Enemy {
    pub id: EntityId,
    pub transform: Transform,
    pub hp: i32,
    pub max_hp: i32,
    pub speed: f32,
    pub state: EntityState,
    pub facing: f32,
    pub damage: i32,
    pub attack_range: f32,
    pub spawn_x: f32,
    pub spawn_y: f32,
    pub fsm: StateMachine,
    pub aggro: AggroTable,
    pub has_hit_this_attack: bool,
    pub windup_timer: f32,    // Attack telegraph timer
    pub parried_timer: f32,   // Parry stagger duration (overrides FSM stagger)
    pub flash_timer: f32,
    pub death_timer: f32,
    pub kind: EnemyKind,
    pub shoot_timer: f32,
    pub shoot_cooldown: f32,
    pub block_chance: f32,
    // Patrol
    pub patrol_timer: f32,
    pub patrol_dir: f32,
    pub patrol_range: f32,
    // Assassin dodge cooldown
    pub dodge_timer: f32,
    pub dodge_dir: f32,
    // Dark Mage teleport
    pub teleport_timer: f32,
    // Mimic
    pub mimic_activated: bool,
    pub grab_timer: f32,
}

impl Enemy {
    pub fn new_hollow_soldier(id: EntityId, x: f32, y: f32) -> Self {
        let mut fsm = StateMachine::new(IDLE);

        // IDLE -> ALERT when target nearby
        fsm.add_state(StateDef {
            id: IDLE,
            name: "Idle".into(),
            duration: None,
            transitions: vec![Transition {
                target: ALERT,
                condition: target_close,
                priority: 1,
            }],
        });

        // ALERT -> CHASE immediately
        fsm.add_state(StateDef {
            id: ALERT,
            name: "Alert".into(),
            duration: Some(0.5),
            transitions: vec![Transition {
                target: CHASE,
                condition: always,
                priority: 1,
            }],
        });

        // CHASE -> ATTACK when close, RETURN when far
        fsm.add_state(StateDef {
            id: CHASE,
            name: "Chase".into(),
            duration: None,
            transitions: vec![
                Transition {
                    target: ATTACK,
                    condition: target_nearby,
                    priority: 2,
                },
                Transition {
                    target: RETURN,
                    condition: target_far,
                    priority: 1,
                },
            ],
        });

        // ATTACK -> CHASE after attack + recovery
        fsm.add_state(StateDef {
            id: ATTACK,
            name: "Attack".into(),
            duration: Some(1.5),
            transitions: vec![Transition {
                target: CHASE,
                condition: attack_done,
                priority: 1,
            }],
        });

        // RETREAT -> CHASE when recovered
        fsm.add_state(StateDef {
            id: RETREAT,
            name: "Retreat".into(),
            duration: Some(1.0),
            transitions: vec![Transition {
                target: CHASE,
                condition: retreat_done,
                priority: 1,
            }],
        });

        // RETURN -> IDLE when back at spawn
        fsm.add_state(StateDef {
            id: RETURN,
            name: "Return".into(),
            duration: None,
            transitions: vec![Transition {
                target: IDLE,
                condition: |ctx| ctx.distance_to_target < 10.0,
                priority: 1,
            }],
        });

        // STAGGERED -> previous after recovery
        fsm.add_state(StateDef {
            id: STAGGERED,
            name: "Staggered".into(),
            duration: Some(0.3),
            transitions: vec![Transition {
                target: CHASE,
                condition: always,
                priority: 1,
            }],
        });

        let aggro = AggroTable::new(300.0, 500.0);

        Self {
            id,
            transform: Transform::new(x, y),
            hp: 300,
            max_hp: 300,
            speed: 70.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 20,
            attack_range: 36.0,
            spawn_x: x,
            spawn_y: y,
            fsm,
            aggro,
            has_hit_this_attack: false,
            windup_timer: 0.0,
            parried_timer: 0.0,
            flash_timer: 0.0,
            death_timer: 0.0,
            kind: EnemyKind::HollowSoldier,
            shoot_timer: 0.0,
            shoot_cooldown: 2.0,
            block_chance: 0.0,
            patrol_timer: 0.0,
            patrol_dir: 1.0,
            patrol_range: 30.0,
            dodge_timer: 0.0,
            dodge_dir: 1.0,
            teleport_timer: 0.0,
            mimic_activated: false,
            grab_timer: 0.0,
        }
    }

    pub fn new_archer(id: EntityId, x: f32, y: f32) -> Self {
        let mut fsm = StateMachine::new(IDLE);

        fsm.add_state(StateDef {
            id: IDLE, name: "Idle".into(), duration: None,
            transitions: vec![Transition { target: ALERT, condition: target_close, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ALERT, name: "Alert".into(), duration: Some(0.5),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: CHASE, name: "Chase".into(), duration: None,
            transitions: vec![
                Transition { target: RANGED_ATTACK, condition: target_in_range, priority: 3 },
                Transition { target: ATTACK, condition: target_nearby, priority: 2 },
                Transition { target: RETURN, condition: target_far, priority: 1 },
            ],
        });
        fsm.add_state(StateDef {
            id: RANGED_ATTACK, name: "RangedAttack".into(), duration: Some(1.0),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ATTACK, name: "Attack".into(), duration: Some(1.5),
            transitions: vec![Transition { target: CHASE, condition: attack_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETURN, name: "Return".into(), duration: None,
            transitions: vec![Transition { target: IDLE, condition: |ctx| ctx.distance_to_target < 10.0, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: STAGGERED, name: "Staggered".into(), duration: Some(0.3),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });

        let aggro = AggroTable::new(350.0, 500.0);
        Self {
            id, transform: Transform::new(x, y),
            hp: 180, max_hp: 180, speed: 50.0,
            state: EntityState::Idle, facing: 0.0,
            damage: 15, attack_range: 32.0,
            spawn_x: x, spawn_y: y, fsm, aggro,
            has_hit_this_attack: false, windup_timer: 0.0, parried_timer: 0.0, flash_timer: 0.0, death_timer: 0.0,
            kind: EnemyKind::Archer,
            shoot_timer: 0.0, shoot_cooldown: 2.0,
            block_chance: 0.0,
            patrol_timer: 0.0,
            patrol_dir: 1.0,
            patrol_range: 25.0,
            dodge_timer: 0.0, dodge_dir: 1.0,
            teleport_timer: 0.0,
            mimic_activated: false, grab_timer: 0.0,
        }
    }

    pub fn new_knight(id: EntityId, x: f32, y: f32) -> Self {
        let mut fsm = StateMachine::new(IDLE);

        fsm.add_state(StateDef {
            id: IDLE, name: "Idle".into(), duration: None,
            transitions: vec![Transition { target: ALERT, condition: target_close, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ALERT, name: "Alert".into(), duration: Some(0.3),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: CHASE, name: "Chase".into(), duration: None,
            transitions: vec![
                Transition { target: ATTACK, condition: |ctx| ctx.distance_to_target < 44.0, priority: 2 },
                Transition { target: RETURN, condition: target_far, priority: 1 },
            ],
        });
        fsm.add_state(StateDef {
            id: ATTACK, name: "Attack".into(), duration: Some(1.8),
            transitions: vec![Transition { target: RETREAT, condition: attack_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETREAT, name: "Retreat".into(), duration: Some(0.8),
            transitions: vec![Transition { target: CHASE, condition: retreat_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETURN, name: "Return".into(), duration: None,
            transitions: vec![Transition { target: IDLE, condition: |ctx| ctx.distance_to_target < 10.0, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: STAGGERED, name: "Staggered".into(), duration: Some(0.2),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });

        let aggro = AggroTable::new(250.0, 450.0);
        Self {
            id, transform: Transform::new(x, y),
            hp: 500, max_hp: 500, speed: 55.0,
            state: EntityState::Idle, facing: 0.0,
            damage: 45, attack_range: 44.0,
            spawn_x: x, spawn_y: y, fsm, aggro,
            has_hit_this_attack: false, windup_timer: 0.0, parried_timer: 0.0, flash_timer: 0.0, death_timer: 0.0,
            kind: EnemyKind::Knight,
            shoot_timer: 0.0, shoot_cooldown: 2.0,
            block_chance: 0.4,
            patrol_timer: 0.0,
            patrol_dir: 1.0,
            patrol_range: 35.0,
            dodge_timer: 0.0, dodge_dir: 1.0,
            teleport_timer: 0.0,
            mimic_activated: false, grab_timer: 0.0,
        }
    }

    pub fn is_fully_dead(&self) -> bool {
        self.is_dead() && self.death_timer <= 0.0
    }

    pub fn new_mini_boss(id: EntityId, x: f32, y: f32) -> Self {
        let mut fsm = StateMachine::new(IDLE);

        fsm.add_state(StateDef {
            id: IDLE, name: "Idle".into(), duration: None,
            transitions: vec![Transition { target: ALERT, condition: target_close, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ALERT, name: "Alert".into(), duration: Some(0.2),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: CHASE, name: "Chase".into(), duration: None,
            transitions: vec![
                Transition { target: ATTACK, condition: |ctx| ctx.distance_to_target < 50.0, priority: 3 },
                Transition { target: RANGED_ATTACK, condition: |ctx| ctx.distance_to_target < 200.0 && ctx.distance_to_target > 80.0 && ctx.can_see_target, priority: 2 },
                Transition { target: RETURN, condition: target_far, priority: 1 },
            ],
        });
        fsm.add_state(StateDef {
            id: RANGED_ATTACK, name: "RangedAttack".into(), duration: Some(0.8),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ATTACK, name: "Attack".into(), duration: Some(2.0),
            transitions: vec![
                Transition { target: RETREAT, condition: low_hp, priority: 2 },
                Transition { target: CHASE, condition: attack_done, priority: 1 },
            ],
        });
        fsm.add_state(StateDef {
            id: RETREAT, name: "Retreat".into(), duration: Some(0.6),
            transitions: vec![Transition { target: CHASE, condition: retreat_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETURN, name: "Return".into(), duration: None,
            transitions: vec![Transition { target: IDLE, condition: |ctx| ctx.distance_to_target < 10.0, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: STAGGERED, name: "Staggered".into(), duration: Some(0.15),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });

        let aggro = AggroTable::new(300.0, 600.0);
        Self {
            id, transform: Transform::new(x, y),
            hp: 800, max_hp: 800, speed: 70.0,
            state: EntityState::Idle, facing: 0.0,
            damage: 55, attack_range: 50.0,
            spawn_x: x, spawn_y: y, fsm, aggro,
            has_hit_this_attack: false, windup_timer: 0.0, parried_timer: 0.0, flash_timer: 0.0, death_timer: 0.0,
            kind: EnemyKind::Knight,
            shoot_timer: 0.0, shoot_cooldown: 1.5,
            block_chance: 0.3,
            patrol_timer: 0.0,
            patrol_dir: 1.0,
            patrol_range: 40.0,
            dodge_timer: 0.0, dodge_dir: 1.0,
            teleport_timer: 0.0,
            mimic_activated: false, grab_timer: 0.0,
        }
    }

    pub fn new_assassin(id: EntityId, x: f32, y: f32) -> Self {
        let mut fsm = StateMachine::new(IDLE);
        fsm.add_state(StateDef {
            id: IDLE, name: "Idle".into(), duration: None,
            transitions: vec![Transition { target: ALERT, condition: target_close, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ALERT, name: "Alert".into(), duration: Some(0.2),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: CHASE, name: "Chase".into(), duration: None,
            transitions: vec![
                Transition { target: ATTACK, condition: |ctx| ctx.distance_to_target < 32.0, priority: 3 },
                Transition { target: RANGED_ATTACK, condition: |ctx| ctx.distance_to_target < 80.0 && ctx.distance_to_target > 30.0, priority: 2 },
                Transition { target: RETURN, condition: target_far, priority: 1 },
            ],
        });
        // RANGED_ATTACK is used for lunge/dodge attack
        fsm.add_state(StateDef {
            id: RANGED_ATTACK, name: "Lunge".into(), duration: Some(0.4),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ATTACK, name: "Backstab".into(), duration: Some(0.8),
            transitions: vec![Transition { target: RETREAT, condition: attack_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETREAT, name: "Retreat".into(), duration: Some(0.5),
            transitions: vec![Transition { target: CHASE, condition: retreat_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETURN, name: "Return".into(), duration: None,
            transitions: vec![Transition { target: IDLE, condition: |ctx| ctx.distance_to_target < 10.0, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: STAGGERED, name: "Staggered".into(), duration: Some(0.2),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });

        let aggro = AggroTable::new(280.0, 500.0);
        Self {
            id, transform: Transform::new(x, y),
            hp: 220, max_hp: 220, speed: 110.0,
            state: EntityState::Idle, facing: 0.0,
            damage: 40, attack_range: 32.0,
            spawn_x: x, spawn_y: y, fsm, aggro,
            has_hit_this_attack: false, windup_timer: 0.0, parried_timer: 0.0, flash_timer: 0.0, death_timer: 0.0,
            kind: EnemyKind::Assassin,
            shoot_timer: 0.0, shoot_cooldown: 1.2,
            block_chance: 0.0,
            patrol_timer: 0.0, patrol_dir: 1.0, patrol_range: 40.0,
            dodge_timer: 1.5, dodge_dir: 1.0,
            teleport_timer: 0.0,
            mimic_activated: false, grab_timer: 0.0,
        }
    }

    pub fn new_dark_mage(id: EntityId, x: f32, y: f32) -> Self {
        let mut fsm = StateMachine::new(IDLE);
        fsm.add_state(StateDef {
            id: IDLE, name: "Idle".into(), duration: None,
            transitions: vec![Transition { target: ALERT, condition: target_close, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ALERT, name: "Alert".into(), duration: Some(0.5),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: CHASE, name: "Chase".into(), duration: None,
            transitions: vec![
                Transition { target: RANGED_ATTACK, condition: |ctx| ctx.distance_to_target < 300.0 && ctx.distance_to_target > 60.0, priority: 3 },
                Transition { target: ATTACK, condition: |ctx| ctx.distance_to_target < 60.0, priority: 2 },
                Transition { target: RETURN, condition: target_far, priority: 1 },
            ],
        });
        fsm.add_state(StateDef {
            id: RANGED_ATTACK, name: "CastSpell".into(), duration: Some(1.2),
            transitions: vec![
                Transition { target: RETREAT, condition: |ctx| ctx.distance_to_target < 80.0, priority: 2 },
                Transition { target: CHASE, condition: always, priority: 1 },
            ],
        });
        fsm.add_state(StateDef {
            id: ATTACK, name: "Melee".into(), duration: Some(1.0),
            transitions: vec![Transition { target: RETREAT, condition: attack_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETREAT, name: "Teleport".into(), duration: Some(0.8),
            transitions: vec![Transition { target: CHASE, condition: retreat_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETURN, name: "Return".into(), duration: None,
            transitions: vec![Transition { target: IDLE, condition: |ctx| ctx.distance_to_target < 10.0, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: STAGGERED, name: "Staggered".into(), duration: Some(0.4),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });

        let aggro = AggroTable::new(350.0, 550.0);
        Self {
            id, transform: Transform::new(x, y),
            hp: 250, max_hp: 250, speed: 40.0,
            state: EntityState::Idle, facing: 0.0,
            damage: 50, attack_range: 60.0,
            spawn_x: x, spawn_y: y, fsm, aggro,
            has_hit_this_attack: false, windup_timer: 0.0, parried_timer: 0.0, flash_timer: 0.0, death_timer: 0.0,
            kind: EnemyKind::DarkMage,
            shoot_timer: 0.0, shoot_cooldown: 2.5,
            block_chance: 0.0,
            patrol_timer: 0.0, patrol_dir: 1.0, patrol_range: 20.0,
            dodge_timer: 0.0, dodge_dir: 1.0,
            teleport_timer: 5.0,
            mimic_activated: false, grab_timer: 0.0,
        }
    }

    pub fn new_mimic(id: EntityId, x: f32, y: f32) -> Self {
        let mut fsm = StateMachine::new(IDLE);
        // Mimic starts in IDLE disguised as chest — activated on player proximity
        fsm.add_state(StateDef {
            id: IDLE, name: "Disguised".into(), duration: None,
            transitions: vec![Transition { target: ALERT, condition: |ctx| ctx.distance_to_target < 40.0, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ALERT, name: "Reveal".into(), duration: Some(0.5),
            transitions: vec![Transition { target: ATTACK, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ATTACK, name: "Grab".into(), duration: Some(1.5),
            transitions: vec![Transition { target: CHASE, condition: attack_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: CHASE, name: "Chase".into(), duration: None,
            transitions: vec![
                Transition { target: ATTACK, condition: |ctx| ctx.distance_to_target < 40.0, priority: 2 },
                Transition { target: RETURN, condition: target_far, priority: 1 },
            ],
        });
        fsm.add_state(StateDef {
            id: RETURN, name: "Return".into(), duration: None,
            transitions: vec![Transition { target: IDLE, condition: |ctx| ctx.distance_to_target < 10.0, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: STAGGERED, name: "Staggered".into(), duration: Some(0.3),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });

        let aggro = AggroTable::new(40.0, 600.0); // Short detection, long memory
        Self {
            id, transform: Transform::new(x, y),
            hp: 600, max_hp: 600, speed: 55.0,
            state: EntityState::Idle, facing: 0.0,
            damage: 70, attack_range: 40.0,
            spawn_x: x, spawn_y: y, fsm, aggro,
            has_hit_this_attack: false, windup_timer: 0.0, parried_timer: 0.0, flash_timer: 0.0, death_timer: 0.0,
            kind: EnemyKind::Mimic,
            shoot_timer: 0.0, shoot_cooldown: 0.0,
            block_chance: 0.0,
            patrol_timer: 0.0, patrol_dir: 1.0, patrol_range: 0.0,
            dodge_timer: 0.0, dodge_dir: 1.0,
            teleport_timer: 0.0,
            mimic_activated: false, grab_timer: 0.0,
        }
    }

    pub fn should_shoot(&mut self, dt: f32) -> bool {
        if self.kind != EnemyKind::Archer && self.kind != EnemyKind::DarkMage { return false; }
        self.shoot_timer -= dt;
        if self.shoot_timer <= 0.0 {
            self.shoot_timer = self.shoot_cooldown;
            return true;
        }
        false
    }

    pub fn try_block(&self) -> bool {
        if self.kind != EnemyKind::Knight && self.kind != EnemyKind::Assassin { return false; }
        let r = (self.id * 1103515245 + 12345) as f32;
        (r % 100.0) < self.block_chance * 100.0
    }

    pub fn tick_death(&mut self, dt: f32) {
        if self.death_timer > 0.0 {
            self.death_timer -= dt;
        }
    }

    pub fn update_ai(&mut self, target_x: f32, target_y: f32, dt: f32, nav_grid: &crate::world::nav_grid::NavGrid, chunk_offset: (f32, f32)) {
        self.aggro.check_detection(
            self.transform.x,
            self.transform.y,
            1,
            target_x,
            target_y,
        );

        let ctx = TransitionContext {
            distance_to_target: if self.aggro.has_target() {
                self.aggro.distance_to_target(self.transform.x, self.transform.y)
            } else {
                f32::MAX
            },
            hp_ratio: self.hp as f32 / self.max_hp as f32,
            stamina_ratio: 1.0,
            state_timer: self.fsm.state_timer,
            can_see_target: self.aggro.can_see_target,
        };

        let new_state = self.fsm.update(dt, &ctx);

        // Tick windup timer
        if self.windup_timer > 0.0 {
            self.windup_timer -= dt;
        }

        // Tick parried timer — keep staggered during riposte window
        if self.parried_timer > 0.0 {
            self.parried_timer -= dt;
            if self.parried_timer > 0.0 {
                self.state = EntityState::Staggered;
                self.fsm.current_state = STAGGERED;
            }
        }

        // Map FSM state to behavior
        match new_state {
            IDLE | RETURN => {
                if new_state == RETURN {
                    let dx = self.spawn_x - self.transform.x;
                    let dy = self.spawn_y - self.transform.y;
                    let dist = (dx * dx + dy * dy).sqrt();
                    if dist > 5.0 {
                        self.facing = dy.atan2(dx);
                        let speed = self.speed * dt;
                        self.transform.x += self.facing.cos() * speed;
                        self.transform.y += self.facing.sin() * speed;
                    }
                } else {
                    // Patrol: walk back and forth near spawn
                    self.patrol_timer += dt;
                    if self.patrol_timer > 2.0 {
                        self.patrol_timer = 0.0;
                        self.patrol_dir = -self.patrol_dir;
                    }
                    let speed = self.speed * 0.3 * dt;
                    let dx = self.transform.x - self.spawn_x;
                    if dx.abs() > self.patrol_range {
                        self.patrol_dir = -dx.signum();
                    }
                    self.transform.x += self.patrol_dir * speed;
                    self.transform.scale_x = if self.patrol_dir < 0.0 { -1.0 } else { 1.0 };
                }
                self.state = EntityState::Idle;
            }
            ALERT => {
                self.state = EntityState::Idle;
                // Face target
                if self.aggro.has_target() {
                    let dx = self.aggro.last_known_x - self.transform.x;
                    let dy = self.aggro.last_known_y - self.transform.y;
                    self.facing = dy.atan2(dx);
                }
            }
            CHASE => {
                if self.aggro.has_target() {
                    let dx = self.aggro.last_known_x - self.transform.x;
                    let dy = self.aggro.last_known_y - self.transform.y;
                    let dist = (dx * dx + dy * dy).sqrt();

                    // Assassin: dodge sideways periodically
                    if self.kind == EnemyKind::Assassin {
                        self.dodge_timer -= dt;
                        if self.dodge_timer <= 0.0 {
                            self.dodge_timer = 2.0 + (self.id as f32 % 1.5);
                            self.dodge_dir = if (self.id as f32) % 2.0 < 1.0 { -1.0 } else { 1.0 };
                            let perp = self.facing + std::f32::consts::FRAC_PI_2 * self.dodge_dir;
                            self.transform.x += perp.cos() * 60.0;
                            self.transform.y += perp.sin() * 60.0;
                        }
                    }

                    // Dark Mage: teleport when low HP
                    if self.kind == EnemyKind::DarkMage {
                        self.teleport_timer -= dt;
                        if self.teleport_timer <= 0.0 && self.hp < self.max_hp * 2 / 3 {
                            self.teleport_timer = 6.0;
                            // Teleport to a random offset
                            let angle = (self.id as f32 * 1.7) % std::f32::consts::TAU;
                            self.transform.x = self.spawn_x + angle.cos() * 120.0;
                            self.transform.y = self.spawn_y + angle.sin() * 120.0;
                            self.flash_timer = 0.3;
                        }
                    }

                    // Mimic: reveal when chasing
                    if self.kind == EnemyKind::Mimic && !self.mimic_activated {
                        self.mimic_activated = true;
                    }

                    // Use pathfinding: find next waypoint toward target
                    let start = nav_grid.world_to_cell(self.transform.x - chunk_offset.0, self.transform.y - chunk_offset.1);
                    let goal = nav_grid.world_to_cell(self.aggro.last_known_x - chunk_offset.0, self.aggro.last_known_y - chunk_offset.1);

                    let move_dir = if dist < 50.0 {
                        dy.atan2(dx)
                    } else if let Some(next) = nav_grid.find_path(start, goal).get(1).copied() {
                        let (wx, wy) = nav_grid.cell_to_world(next);
                        let nwx = wx + chunk_offset.0;
                        let nwy = wy + chunk_offset.1;
                        let ndx = nwx - self.transform.x;
                        let ndy = nwy - self.transform.y;
                        ndy.atan2(ndx)
                    } else {
                        dy.atan2(dx)
                    };

                    self.facing = move_dir;
                    let speed = self.speed * dt;
                    self.transform.x += self.facing.cos() * speed;
                    self.transform.y += self.facing.sin() * speed;
                    self.transform.scale_x = if self.facing.cos() < 0.0 { -1.0 } else { 1.0 };
                }
                self.state = EntityState::Moving;
            }
            ATTACK => {
                if self.state != EntityState::Attacking {
                    self.has_hit_this_attack = false;
                    self.windup_timer = 0.5; // Telegraph before hit
                }
                self.state = EntityState::Attacking;
            }
            RANGED_ATTACK => {
                self.state = EntityState::Attacking;
                if self.aggro.has_target() {
                    let dx = self.aggro.last_known_x - self.transform.x;
                    let dy = self.aggro.last_known_y - self.transform.y;
                    self.facing = dy.atan2(dx);
                }
            }
            RETREAT => {
                if self.aggro.has_target() {
                    let dx = self.transform.x - self.aggro.last_known_x;
                    let dy = self.transform.y - self.aggro.last_known_y;
                    self.facing = dy.atan2(dx);
                    let speed = self.speed * 0.5 * dt;
                    self.transform.x += self.facing.cos() * speed;
                    self.transform.y += self.facing.sin() * speed;
                }
                self.state = EntityState::Moving;
            }
            STAGGERED => {
                self.state = EntityState::Staggered;
            }
            DEAD => {
                self.state = EntityState::Dead;
            }
            _ => {}
        }
    }
}

impl Entity for Enemy {
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

    fn update(&mut self, _dt: f32) {
        // AI update is called separately with target position
    }

    fn render(&self, batcher: &mut SpriteBatcher, texture: &Texture, gl: &GL) {
        if self.death_timer <= 0.0 && self.is_dead() {
            return;
        }
        let (size, base_color) = match self.kind {
            EnemyKind::HollowSoldier => (28.0, [0.6, 0.6, 0.6, 1.0]),
            EnemyKind::Archer => (24.0, [0.4, 0.7, 0.3, 1.0]),
            EnemyKind::Knight => (34.0, [0.5, 0.5, 0.7, 1.0]),
            EnemyKind::Assassin => (22.0, [0.2, 0.2, 0.3, 1.0]),
            EnemyKind::DarkMage => (30.0, [0.5, 0.2, 0.8, 1.0]),
            EnemyKind::Mimic => {
                if !self.mimic_activated {
                    // Disguised as a treasure chest (golden box)
                    let instance = self.transform.to_instance_data(28.0, 24.0, [0.0, 0.0, 1.0, 1.0], [0.8, 0.7, 0.2, 1.0]);
                    batcher.draw(instance, texture, gl);
                    return;
                }
                (38.0, [0.6, 0.4, 0.1, 1.0])
            },
        };
        if self.flash_timer > 0.0 {
            let instance = self.transform.to_instance_data(size, size, [0.0, 0.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0]);
            batcher.draw(instance, texture, gl);
            return;
        }
        let color = match self.state {
            EntityState::Dead => {
                let alpha = (self.death_timer / 1.0).max(0.0);
                [0.3, 0.3, 0.3, alpha]
            }
            EntityState::Idle => base_color,
            EntityState::Moving => [base_color[0] + 0.1, base_color[1], base_color[2] - 0.1, 1.0],
            EntityState::Attacking => {
                if self.windup_timer > 0.0 {
                    // Telegraph: pulsing yellow-orange during windup
                    let pulse = (self.windup_timer * 12.0).sin() * 0.3 + 0.7;
                    [1.0, pulse, 0.0, 1.0]
                } else {
                    [1.0, 0.3, 0.3, 1.0]
                }
            }
            EntityState::Staggered => [1.0, 0.5, 0.0, 1.0],
            _ => base_color,
        };
        let draw_size = if self.windup_timer > 0.0 && self.state == EntityState::Attacking {
            size * (1.0 + self.windup_timer * 0.4) // Grow during windup
        } else {
            size
        };
        let instance = self.transform.to_instance_data(draw_size, draw_size, [0.0, 0.0, 1.0, 1.0], color);
        batcher.draw(instance, texture, gl);
    }

    fn take_damage(&mut self, info: &DamageInfo) {
        self.hp -= info.damage;
        self.flash_timer = 0.12;
        self.aggro.add_threat(info.damage as f32 * 2.0);
        self.fsm.current_state = STAGGERED;
        self.fsm.state_timer = 0.0;
        self.state = EntityState::Staggered;
        if self.hp <= 0 {
            self.hp = 0;
            self.fsm.current_state = DEAD;
            self.state = EntityState::Dead;
            self.death_timer = 1.0;
        }
    }

    fn is_dead(&self) -> bool {
        self.hp <= 0
    }
}
