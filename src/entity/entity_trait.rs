use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use web_sys::WebGl2RenderingContext as GL;

pub type EntityId = u64;

#[derive(Clone, Debug, PartialEq)]
pub enum EntityState {
    Idle,
    Moving,
    Attacking,
    Rolling,
    Blocking,
    Staggered,
    Dead,
}

pub struct DamageInfo {
    pub damage: i32,
    pub knockback_x: f32,
    pub knockback_y: f32,
    pub poise_damage: f32,
    pub attacker_id: EntityId,
}

pub trait Entity {
    fn id(&self) -> EntityId;
    fn position(&self) -> (f32, f32);
    fn set_position(&mut self, x: f32, y: f32);
    fn hp(&self) -> i32;
    fn max_hp(&self) -> i32;
    fn state(&self) -> &EntityState;
    fn update(&mut self, dt: f32);
    fn render(&self, batcher: &mut SpriteBatcher, texture: &Texture, gl: &GL);
    fn take_damage(&mut self, info: &DamageInfo);
    fn is_dead(&self) -> bool {
        self.hp() <= 0
    }
}
