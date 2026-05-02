use crate::combat::stamina::StaminaPool;
use crate::combat::weapon::{Weapon, WeaponType};
use crate::core::transform::Transform;
use crate::entity::entity_trait::{AttackTracker, DamageInfo, DamageOutcome, Entity, EntityId, EntityState};
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use crate::rpg::equipment::Equipment;
use web_sys::WebGl2RenderingContext as GL;

pub struct Player {
    pub id: EntityId,
    pub transform: Transform,
    pub hp: i32,
    pub max_hp: i32,
    pub speed: f32,
    pub state: EntityState,
    pub facing: f32,
    pub move_dir: f32,
    // Combat state
    pub attack_timer: f32,
    pub attack_duration: f32,
    pub is_heavy_attack: bool,
    pub attack_tracker: AttackTracker,
    pub heavy_attack_duration: f32,
    pub roll_timer: f32,
    pub roll_duration: f32,
    pub stagger_timer: f32,
    pub invuln_timer: f32,
    pub flash_timer: f32,
    pub parry_timer: f32,
    pub block_timer: f32,
    pub parry_window: f32,
    pub stamina: StaminaPool,
    // RPG stats
    pub level: u32,
    pub vigor: u32,      // increases HP
    pub endurance: u32,  // increases stamina
    pub strength: u32,   // increases damage
    // Weapon system
    pub weapon: Weapon,
    pub alt_weapon: Option<Weapon>,
    // Equipment
    pub equipment: Equipment,
    // Status effects
    pub poison_timer: f32,
    pub poison_tick: f32,
}

impl Player {
    pub fn new(id: EntityId, x: f32, y: f32) -> Self {
        Self {
            id,
            transform: Transform::new(x, y),
            hp: 600,
            max_hp: 600,
            speed: 240.0,
            state: EntityState::Idle,
            facing: 0.0,
            move_dir: 0.0,
            attack_timer: 0.0,
            attack_duration: 0.3,
            is_heavy_attack: false,
            attack_tracker: AttackTracker::new(),
            heavy_attack_duration: 0.6,
            roll_timer: 0.0,
            roll_duration: 0.35,
            stagger_timer: 0.0,
            invuln_timer: 0.0,
            flash_timer: 0.0,
            parry_timer: 0.0,
            block_timer: 0.0,
            parry_window: 0.25,
            stamina: StaminaPool::new(100.0),
            level: 1,
            vigor: 5,
            endurance: 5,
            strength: 5,
            weapon: Weapon::longsword(),
            alt_weapon: None,
            equipment: Equipment::default(),
            poison_timer: 0.0,
            poison_tick: 0.0,
        }
    }

    pub fn damage(&self) -> i32 {
        let base = self.weapon.base_damage;
        let scaling = (self.strength as f32 * self.weapon.strength_scaling
            + self.endurance as f32 * self.weapon.dexterity_scaling) * 2.0;
        let bonus = 1.0 + self.equipment.damage_bonus();
        ((base as f32 + scaling) * bonus) as i32
    }

    /// Light attack stamina cost from weapon moveset.
    pub fn light_stamina_cost(&self) -> f32 {
        self.weapon.get_moveset().light_attack_chain()[0].stamina_cost
    }

    /// Heavy attack stamina cost from weapon moveset.
    pub fn heavy_stamina_cost(&self) -> f32 {
        self.weapon.get_moveset().heavy_attack().stamina_cost
    }

    /// Light attack duration based on weapon moveset recovery frames.
    pub fn light_attack_duration(&self) -> f32 {
        let moveset = self.weapon.get_moveset();
        let frames = moveset.light_attack_chain().get(0).map(|f| f.recovery_frames).unwrap_or(18);
        frames as f32 / 60.0
    }

    /// Heavy attack duration based on weapon moveset recovery frames.
    pub fn heavy_attack_duration(&self) -> f32 {
        let frames = self.weapon.get_moveset().heavy_attack().recovery_frames;
        frames as f32 / 60.0
    }

    /// Swap primary and alt weapons. If no alt weapon, swap to fist.
    pub fn swap_weapon(&mut self) {
        if let Some(alt) = self.alt_weapon.take() {
            let old = std::mem::replace(&mut self.weapon, alt);
            self.alt_weapon = Some(old);
        } else if self.weapon.weapon_type != WeaponType::Fist {
            let old = std::mem::replace(&mut self.weapon, Weapon::fist());
            self.alt_weapon = Some(old);
        }
    }

    /// Roll speed affected by equip load
    pub fn roll_speed_multiplier(&self) -> f32 {
        let load = self.equipment.equip_load_percent(40.0 + self.vitality() as f32 * 1.5);
        if load < 0.3 { 1.3 }
        else if load < 0.7 { 1.0 }
        else { 0.6 }
    }

    fn vitality(&self) -> u32 {
        10 // Base vitality — could be a stat
    }

    pub fn level_up_cost(&self) -> u32 {
        self.level * 100
    }

    pub fn apply_stats(&mut self) {
        let hp_bonus = self.equipment.hp_bonus();
        self.max_hp = (600.0 + ((self.vigor - 5) as f32) * 50.0) as i32;
        self.max_hp = (self.max_hp as f32 * (1.0 + hp_bonus)) as i32;
        self.stamina.maximum = 100.0 + ((self.endurance - 5) as f32) * 15.0;
        self.stamina.current = self.stamina.current.min(self.stamina.maximum);
    }

    pub fn is_parrying(&self) -> bool {
        self.state == EntityState::Blocking && self.parry_timer > 0.0
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
        let regen_bonus = self.equipment.stamina_regen_bonus();
        self.stamina.update_with_bonus(dt, is_acting, regen_bonus);
        if self.invuln_timer > 0.0 {
            self.invuln_timer -= dt;
        }
        if self.flash_timer > 0.0 {
            self.flash_timer -= dt;
        }
        // Poison tick
        if self.poison_timer > 0.0 {
            self.poison_timer -= dt;
            self.poison_tick -= dt;
            if self.poison_tick <= 0.0 {
                self.poison_tick = 0.5; // Damage every 0.5s
                self.hp -= 5;
                if self.hp <= 0 {
                    self.hp = 0;
                    self.state = EntityState::Dead;
                }
            }
        }

        match self.state {
            EntityState::Moving => {
                let speed = self.speed * dt;
                self.transform.x += self.move_dir.cos() * speed;
                self.transform.y += self.move_dir.sin() * speed;
                if self.facing.cos() < 0.0 {
                    self.transform.scale_x = -1.0;
                } else {
                    self.transform.scale_x = 1.0;
                }
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
                    self.is_heavy_attack = false;
                    self.attack_tracker.reset();
                    self.state = EntityState::Idle;
                }
            }
            EntityState::Staggered => {
                self.stagger_timer -= dt;
                if self.stagger_timer <= 0.0 {
                    self.state = EntityState::Idle;
                }
            }
            EntityState::Blocking => {
                if self.parry_timer > 0.0 {
                    self.parry_timer -= dt;
                }
                if self.block_timer > 0.0 {
                    self.block_timer -= dt;
                    if self.block_timer <= 0.0 {
                        self.state = EntityState::Idle;
                    }
                }
            }
            _ => {}
        }
    }

    fn render(&self, batcher: &mut SpriteBatcher, texture: &Texture, gl: &GL) {
        let (frame, color) = match self.state {
            EntityState::Idle => (0, [1.0, 1.0, 1.0, 1.0]),
            EntityState::Moving => (1, [1.0, 1.0, 0.9, 1.0]),
            EntityState::Attacking => {
                if self.is_heavy_attack {
                    (2, [1.0, 0.8, 0.2, 1.0])
                } else {
                    (2, [1.0, 0.4, 0.4, 1.0])
                }
            }
            EntityState::Rolling => (1, [0.4, 0.7, 1.0, 0.7]),
            EntityState::Blocking => {
                if self.parry_timer > 0.0 {
                    (3, [0.2, 1.0, 1.0, 1.0])
                } else {
                    (3, [0.5, 0.5, 0.8, 1.0])
                }
            }
            EntityState::Staggered => (0, [1.0, 0.2, 0.2, 1.0]),
            EntityState::Dead => (0, [0.3, 0.3, 0.3, 0.5]),
        };

        if self.flash_timer > 0.0 {
            let uv = [frame as f32 * 0.25, 0.0, (frame + 1) as f32 * 0.25, 1.0];
            let instance = self.transform.to_instance_data(32.0, 32.0, uv, [1.0, 1.0, 1.0, 1.0]);
            batcher.draw(instance, texture, gl);
            return;
        }

        // Green tint when poisoned
        let color = if self.poison_timer > 0.0 {
            [color[0] * 0.5, color[1], color[2] * 0.5, color[3]]
        } else {
            color
        };

        let uv = [frame as f32 * 0.25, 0.0, (frame + 1) as f32 * 0.25, 1.0];
        let instance = self.transform.to_instance_data(32.0, 32.0, uv, color);
        batcher.draw(instance, texture, gl);
    }

    fn take_damage(&mut self, info: &DamageInfo) -> DamageOutcome {
        if self.invuln_timer > 0.0 {
            return DamageOutcome::ignored(info.damage);
        }

        if self.state == EntityState::Blocking && self.parry_timer > 0.0 && info.parryable {
            self.flash_timer = 0.15;
            return DamageOutcome::parried(info.damage);
        }

        if self.state == EntityState::Blocking {
            let actual = (info.damage as f32 * 0.3).max(1.0) as i32;
            self.hp -= actual;
            self.stamina.consume(15.0);
            self.flash_timer = 0.1;
            let killed = self.hp <= 0;
            if killed {
                self.hp = 0;
                self.state = EntityState::Dead;
            }
            return DamageOutcome::blocked(info.damage, actual, killed);
        }

        let defense = self.equipment.total_defense();
        let actual = (info.damage as f32 - defense).max(1.0) as i32;
        self.hp -= actual;
        self.state = EntityState::Staggered;
        self.stagger_timer = 0.2;
        self.invuln_timer = 0.8;
        self.flash_timer = 0.12;
        let killed = self.hp <= 0;
        if killed {
            self.hp = 0;
            self.state = EntityState::Dead;
        }
        DamageOutcome::applied(info.damage, actual, killed)
    }

    fn is_dead(&self) -> bool {
        self.hp <= 0
    }
}
