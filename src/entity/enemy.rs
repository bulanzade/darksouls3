use crate::ai::aggro::AggroTable;
use crate::ai::state_machine::*;
use crate::core::transform::Transform;
use crate::entity::entity_trait::{DamageInfo, Entity, EntityId, EntityState};
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use web_sys::WebGl2RenderingContext as GL;

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

        // ATTACK -> CHASE after attack animation
        fsm.add_state(StateDef {
            id: ATTACK,
            name: "Attack".into(),
            duration: Some(0.6),
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

        let aggro = AggroTable::new(200.0, 350.0);

        Self {
            id,
            transform: Transform::new(x, y),
            hp: 200,
            max_hp: 200,
            speed: 60.0,
            state: EntityState::Idle,
            facing: 0.0,
            damage: 30,
            attack_range: 36.0,
            spawn_x: x,
            spawn_y: y,
            fsm,
            aggro,
        }
    }

    pub fn update_ai(&mut self, target_x: f32, target_y: f32, dt: f32) {
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
                    self.facing = dy.atan2(dx);
                    let speed = self.speed * dt;
                    self.transform.x += self.facing.cos() * speed;
                    self.transform.y += self.facing.sin() * speed;
                }
                self.state = EntityState::Moving;
            }
            ATTACK => {
                self.state = EntityState::Attacking;
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
        let color = match self.state {
            EntityState::Idle => [0.6, 0.6, 0.6, 1.0],
            EntityState::Moving => [0.7, 0.6, 0.4, 1.0],
            EntityState::Attacking => [1.0, 0.3, 0.3, 1.0],
            EntityState::Staggered => [1.0, 0.5, 0.0, 1.0],
            EntityState::Dead => [0.3, 0.3, 0.3, 0.3],
            _ => [0.6, 0.6, 0.6, 1.0],
        };
        let instance =
            self.transform
                .to_instance_data(28.0, 28.0, [0.0, 0.0, 1.0, 1.0], color);
        batcher.draw(instance, texture, gl);
    }

    fn take_damage(&mut self, info: &DamageInfo) {
        self.hp -= info.damage;
        self.aggro.add_threat(info.damage as f32 * 2.0);
        self.fsm.current_state = STAGGERED;
        self.fsm.state_timer = 0.0;
        self.state = EntityState::Staggered;
        if self.hp <= 0 {
            self.hp = 0;
            self.fsm.current_state = DEAD;
            self.state = EntityState::Dead;
        }
    }

    fn is_dead(&self) -> bool {
        self.hp <= 0
    }
}
