use crate::combat::stamina::StaminaPool;
use crate::core::input::{InputState, KeyCode};
use crate::core::transform::Transform;
use crate::entity::entity_trait::{DamageInfo, Entity, EntityId, EntityState};
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use web_sys::WebGl2RenderingContext as GL;

pub struct Player {
    pub id: EntityId,
    pub transform: Transform,
    pub hp: i32,
    pub max_hp: i32,
    pub speed: f32,
    pub state: EntityState,
    pub facing: f32,
    // Combat state
    pub attack_timer: f32,
    pub attack_duration: f32,
    pub roll_timer: f32,
    pub roll_duration: f32,
    pub stagger_timer: f32,
    pub invuln_timer: f32,
    pub stamina: StaminaPool,
}

impl Player {
    pub fn new(id: EntityId, x: f32, y: f32) -> Self {
        Self {
            id,
            transform: Transform::new(x, y),
            hp: 500,
            max_hp: 500,
            speed: 120.0,
            state: EntityState::Idle,
            facing: 0.0,
            attack_timer: 0.0,
            attack_duration: 0.3,
            roll_timer: 0.0,
            roll_duration: 0.25,
            stagger_timer: 0.0,
            invuln_timer: 0.0,
            stamina: StaminaPool::new(100.0),
        }
    }

    pub fn handle_input(&mut self, input: &InputState) {
        match self.state {
            EntityState::Idle | EntityState::Moving => {
                let (mx, my) = input.movement();
                if mx != 0.0 || my != 0.0 {
                    self.facing = my.atan2(mx);
                    self.state = EntityState::Moving;
                } else {
                    self.state = EntityState::Idle;
                }

                if input.pressed(KeyCode::Space) {
                    if self.stamina.consume(25.0) {
                        self.state = EntityState::Rolling;
                        self.roll_timer = self.roll_duration;
                    }
                }
                if input.pressed(KeyCode::J) {
                    if self.stamina.consume(20.0) {
                        self.state = EntityState::Attacking;
                        self.attack_timer = self.attack_duration;
                    }
                }
            }
            _ => {} // Can't act during attack/roll/stagger/dead
        }
    }
}

impl Entity for Player {
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

    fn update(&mut self, dt: f32) {
        let is_acting = matches!(self.state, EntityState::Attacking | EntityState::Rolling | EntityState::Blocking);
        self.stamina.update(dt, is_acting);
        if self.invuln_timer > 0.0 {
            self.invuln_timer -= dt;
        }

        match self.state {
            EntityState::Moving => {
                let speed = self.speed * dt;
                self.transform.x += self.facing.cos() * speed;
                self.transform.y += self.facing.sin() * speed;
            }
            EntityState::Rolling => {
                self.roll_timer -= dt;
                let speed = self.speed * 2.0 * dt;
                self.transform.x += self.facing.cos() * speed;
                self.transform.y += self.facing.sin() * speed;
                if self.roll_timer <= 0.0 {
                    self.state = EntityState::Idle;
                }
            }
            EntityState::Attacking => {
                self.attack_timer -= dt;
                if self.attack_timer <= 0.0 {
                    self.state = EntityState::Idle;
                }
            }
            EntityState::Staggered => {
                self.stagger_timer -= dt;
                if self.stagger_timer <= 0.0 {
                    self.state = EntityState::Idle;
                }
            }
            _ => {}
        }
    }

    fn render(&self, batcher: &mut SpriteBatcher, texture: &Texture, gl: &GL) {
        let color = match self.state {
            EntityState::Idle => [1.0, 1.0, 1.0, 1.0],
            EntityState::Moving => [0.9, 0.9, 0.7, 1.0],
            EntityState::Attacking => [1.0, 0.4, 0.4, 1.0],
            EntityState::Rolling => [0.4, 0.7, 1.0, 0.7],
            EntityState::Staggered => [1.0, 0.2, 0.2, 1.0],
            EntityState::Dead => [0.3, 0.3, 0.3, 0.5],
            _ => [1.0, 1.0, 1.0, 1.0],
        };

        let instance = self.transform.to_instance_data(32.0, 32.0, [0.0, 0.0, 1.0, 1.0], color);
        batcher.draw(instance, texture, gl);
    }

    fn take_damage(&mut self, info: &DamageInfo) {
        if self.invuln_timer > 0.0 {
            return;
        }
        self.hp -= info.damage;
        self.state = EntityState::Staggered;
        self.stagger_timer = 0.2;
        self.invuln_timer = 0.8;
        if self.hp <= 0 {
            self.hp = 0;
            self.state = EntityState::Dead;
        }
    }

    fn is_dead(&self) -> bool {
        self.hp <= 0
    }
}
