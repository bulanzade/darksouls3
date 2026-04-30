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
    pub parryable: bool,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct DamageOutcome {
    pub requested_damage: i32,
    pub actual_damage: i32,
    pub was_blocked: bool,
    pub was_parried: bool,
    pub was_ignored: bool,
    pub killed: bool,
}

impl DamageOutcome {
    pub fn ignored(requested_damage: i32) -> Self {
        Self { requested_damage, was_ignored: true, ..Self::default() }
    }

    pub fn applied(requested_damage: i32, actual_damage: i32, killed: bool) -> Self {
        Self { requested_damage, actual_damage, killed, ..Self::default() }
    }

    pub fn blocked(requested_damage: i32, actual_damage: i32, killed: bool) -> Self {
        Self { requested_damage, actual_damage, was_blocked: true, killed, ..Self::default() }
    }

    pub fn parried(requested_damage: i32) -> Self {
        Self { requested_damage, was_parried: true, was_ignored: true, ..Self::default() }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AttackTarget {
    Enemy(EntityId),
    Boss(EntityId),
}

const MAX_ATTACK_TARGETS: usize = 8;

#[derive(Clone, Debug)]
pub struct AttackTracker {
    targets_hit: [Option<AttackTarget>; MAX_ATTACK_TARGETS],
}

impl AttackTracker {
    pub fn new() -> Self {
        Self { targets_hit: [None; MAX_ATTACK_TARGETS] }
    }

    pub fn begin_attack(&mut self) {
        self.reset();
    }

    pub fn reset(&mut self) {
        self.targets_hit = [None; MAX_ATTACK_TARGETS];
    }

    pub fn has_hit(&self, target: AttackTarget) -> bool {
        self.targets_hit.iter().any(|entry| *entry == Some(target))
    }

    pub fn mark_hit(&mut self, target: AttackTarget) {
        if self.has_hit(target) {
            return;
        }
        if let Some(slot) = self.targets_hit.iter_mut().find(|entry| entry.is_none()) {
            *slot = Some(target);
        }
    }
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
    fn take_damage(&mut self, info: &DamageInfo) -> DamageOutcome;
    fn is_dead(&self) -> bool {
        self.hp() <= 0
    }
}
