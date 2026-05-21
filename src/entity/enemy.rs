use crate::ai::aggro::AggroTable;
use crate::ai::state_machine::*;
use crate::core::transform::Transform;
use crate::entity::entity_trait::{DamageInfo, DamageOutcome, Entity, EntityId, EntityState};
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
    CrystalLizard,
    MiniBoss,
    // DS3-specific
    SilverKnight,
    BlackKnight,
    DeepAccursed,
    Evangelist,
    Thrall,
    LothricKnight,
    WingedKnight,
    Ghru,
    Darkwraith,
    Skeleton,
    Jailer,
    SerpentMan,
    Deacon,
    FireDemon,
    StarvedHound,
    PusOfMan,
    CathedralKnight,
    ManGrub,
    Gargoyle,
    Dog,
    Basilisk,
    DemonStatue,
    InfestedCorpse,
    Wretch,
    PeasantHollow,
    GiantSlave,
    HollowAssassin,
    CathedralGraveWarden,
    Rat,
    LargeHollowSoldier,
}

pub struct EnemyBehavior {
    pub can_block: bool,
    pub can_shoot: bool,
    pub parryable_in_attack: bool,
}

impl EnemyKind {
    pub fn behavior_flags(&self) -> EnemyBehavior {
        match self {
            // Ranged + blocking: SilverKnight, SerpentMan can do both
            Self::SilverKnight | Self::SerpentMan
            => EnemyBehavior { can_block: true, can_shoot: true, parryable_in_attack: true },
            // Ranged enemies: can shoot, parryable when attacking
            Self::Archer | Self::DarkMage
            | Self::Deacon | Self::Jailer
            | Self::Basilisk | Self::DemonStatue
            => EnemyBehavior { can_block: false, can_shoot: true, parryable_in_attack: true },
            // Blocking melee: can block, parryable
            Self::Knight | Self::Assassin
            | Self::BlackKnight
            | Self::LothricKnight | Self::WingedKnight
            | Self::CathedralKnight | Self::Darkwraith
            | Self::Gargoyle
            => EnemyBehavior { can_block: true, can_shoot: false, parryable_in_attack: true },
            // Special: Mimic not parryable
            Self::Mimic => EnemyBehavior { can_block: false, can_shoot: false, parryable_in_attack: false },
            // Crystal Lizard: parryable but no block/shoot
            Self::CrystalLizard => EnemyBehavior { can_block: false, can_shoot: false, parryable_in_attack: true },
            // All other melee enemies: parryable when attacking
            _ => EnemyBehavior { can_block: false, can_shoot: false, parryable_in_attack: true },
        }
    }

    /// Stats for DS3-specific enemy kinds: (hp, damage, speed, block_chance, attack_range)
    pub fn ds3_stats(&self) -> (i32, i32, f32, f32, f32) {
        match self {
            Self::SilverKnight => (500, 50, 55.0, 0.5, 54.0),
            Self::BlackKnight => (600, 55, 50.0, 0.6, 54.0),
            Self::DeepAccursed => (900, 60, 35.0, 0.0, 60.0),
            Self::Evangelist => (400, 40, 50.0, 0.2, 54.0),
            Self::Thrall => (150, 30, 130.0, 0.0, 40.0),
            Self::LothricKnight => (450, 48, 55.0, 0.45, 54.0),
            Self::WingedKnight => (550, 55, 45.0, 0.5, 54.0),
            Self::Ghru => (250, 25, 80.0, 0.0, 44.0),
            Self::Darkwraith => (500, 55, 55.0, 0.4, 54.0),
            Self::Skeleton => (200, 25, 80.0, 0.0, 44.0),
            Self::Jailer => (400, 50, 40.0, 0.3, 54.0),
            Self::SerpentMan => (450, 50, 60.0, 0.4, 54.0),
            Self::Deacon => (200, 35, 50.0, 0.0, 48.0),
            Self::FireDemon => (700, 60, 35.0, 0.0, 60.0),
            Self::StarvedHound => (150, 25, 120.0, 0.0, 40.0),
            Self::PusOfMan => (500, 50, 45.0, 0.0, 55.0),
            Self::CathedralKnight => (500, 50, 50.0, 0.5, 54.0),
            Self::ManGrub => (250, 25, 60.0, 0.0, 44.0),
            Self::Gargoyle => (500, 50, 50.0, 0.3, 54.0),
            Self::Dog => (100, 20, 140.0, 0.0, 36.0),
            Self::Basilisk => (200, 30, 55.0, 0.0, 48.0),
            Self::DemonStatue => (350, 45, 50.0, 0.0, 48.0),
            Self::InfestedCorpse => (100, 10, 30.0, 0.0, 44.0),
            Self::Wretch => (280, 40, 100.0, 0.0, 40.0),
            Self::PeasantHollow => (180, 15, 55.0, 0.0, 44.0),
            Self::Mimic => (500, 55, 50.0, 0.4, 54.0),
            Self::GiantSlave => (800, 70, 30.0, 0.0, 60.0),
            Self::HollowAssassin => (200, 30, 110.0, 0.0, 40.0),
            Self::CathedralGraveWarden => (350, 45, 55.0, 0.3, 54.0),
            Self::Rat => (80, 10, 150.0, 0.0, 30.0),
            Self::LargeHollowSoldier => (350, 40, 45.0, 0.3, 54.0),
            _ => (300, 35, 55.0, 0.0, 48.0), // fallback for base kinds
        }
    }

    pub fn soul_reward(&self) -> u32 {
        match self {
            Self::HollowSoldier => 100,
            Self::Archer => 150,
            Self::Knight => 200,
            Self::Assassin => 250,
            Self::DarkMage => 300,
            Self::Mimic => 500,
            Self::CrystalLizard => 1200,
            Self::MiniBoss => 400,
            Self::SilverKnight => 400,
            Self::BlackKnight => 500,
            Self::DeepAccursed => 600,
            Self::Evangelist => 300,
            Self::Thrall => 150,
            Self::LothricKnight => 350,
            Self::WingedKnight => 450,
            Self::Ghru => 200,
            Self::Darkwraith => 400,
            Self::Skeleton => 150,
            Self::Jailer => 350,
            Self::SerpentMan => 400,
            Self::Deacon => 180,
            Self::FireDemon => 500,
            Self::StarvedHound => 120,
            Self::PusOfMan => 350,
            Self::CathedralKnight => 400,
            Self::ManGrub => 200,
            Self::Gargoyle => 350,
            Self::Dog => 80,
            Self::Basilisk => 200,
            Self::DemonStatue => 300,
            Self::InfestedCorpse => 50,
            Self::Wretch => 250,
            Self::PeasantHollow => 80,
            Self::GiantSlave => 500,
            Self::HollowAssassin => 200,
            Self::CathedralGraveWarden => 350,
            Self::Rat => 30,
            Self::LargeHollowSoldier => 250,
        }
    }
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
    pub can_block: bool,
    pub can_shoot: bool,
    pub parryable_in_attack: bool,
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
    fn draw_part(
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
        let instance = transform.to_instance_data(w, h, [0.0, 0.0, 1.0, 1.0], color);
        batcher.draw(instance, texture, gl);
    }

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
            can_block: false, can_shoot: false, parryable_in_attack: true,
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
            can_block: false, can_shoot: true, parryable_in_attack: true,
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
            can_block: true, can_shoot: false, parryable_in_attack: true,
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
            kind: EnemyKind::MiniBoss,
            can_block: true, can_shoot: false, parryable_in_attack: true,
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
            can_block: true, can_shoot: false, parryable_in_attack: true,
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
            can_block: false, can_shoot: true, parryable_in_attack: true,
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
            can_block: false, can_shoot: false, parryable_in_attack: false,
            shoot_timer: 0.0, shoot_cooldown: 0.0,
            block_chance: 0.0,
            patrol_timer: 0.0, patrol_dir: 1.0, patrol_range: 0.0,
            dodge_timer: 0.0, dodge_dir: 1.0,
            teleport_timer: 0.0,
            mimic_activated: false, grab_timer: 0.0,
        }
    }

    pub fn new_crystal_lizard(id: EntityId, x: f32, y: f32) -> Self {
        let mut fsm = StateMachine::new(IDLE);

        fsm.add_state(StateDef {
            id: IDLE, name: "Burrowed".into(), duration: None,
            transitions: vec![Transition { target: ALERT, condition: target_close, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ALERT, name: "Awaken".into(), duration: Some(0.35),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: CHASE, name: "Skitter".into(), duration: None,
            transitions: vec![
                Transition { target: ATTACK, condition: |ctx| ctx.distance_to_target < 58.0, priority: 3 },
                Transition { target: RANGED_ATTACK, condition: |ctx| ctx.distance_to_target >= 58.0 && ctx.distance_to_target < 230.0 && ctx.can_see_target, priority: 2 },
                Transition { target: RETURN, condition: target_far, priority: 1 },
            ],
        });
        fsm.add_state(StateDef {
            id: RANGED_ATTACK, name: "RollingCharge".into(), duration: Some(1.05),
            transitions: vec![Transition { target: RETREAT, condition: always, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: ATTACK, name: "TailSweep".into(), duration: Some(1.0),
            transitions: vec![Transition { target: RETREAT, condition: attack_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETREAT, name: "Recoil".into(), duration: Some(0.55),
            transitions: vec![Transition { target: CHASE, condition: retreat_done, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: RETURN, name: "Return".into(), duration: None,
            transitions: vec![Transition { target: IDLE, condition: |ctx| ctx.distance_to_target < 10.0, priority: 1 }],
        });
        fsm.add_state(StateDef {
            id: STAGGERED, name: "Cracked".into(), duration: Some(0.18),
            transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }],
        });

        let aggro = AggroTable::new(260.0, 560.0);
        Self {
            id, transform: Transform::new(x, y),
            hp: 900, max_hp: 900, speed: 92.0,
            state: EntityState::Idle, facing: 0.0,
            damage: 42, attack_range: 54.0,
            spawn_x: x, spawn_y: y, fsm, aggro,
            has_hit_this_attack: false, windup_timer: 0.0, parried_timer: 0.0, flash_timer: 0.0, death_timer: 0.0,
            kind: EnemyKind::CrystalLizard,
            can_block: false, can_shoot: false, parryable_in_attack: true,
            shoot_timer: 0.0, shoot_cooldown: 0.0,
            block_chance: 0.0,
            patrol_timer: 0.0, patrol_dir: 1.0, patrol_range: 26.0,
            dodge_timer: 0.0, dodge_dir: 1.0,
            teleport_timer: 0.0,
            mimic_activated: false, grab_timer: 0.0,
        }
    }

    /// Create any DS3-specific enemy kind with configured stats from ds3_stats().
    pub fn new_ds3(id: EntityId, x: f32, y: f32, kind: EnemyKind) -> Self {
        let (hp, damage, speed, block_chance, attack_range) = kind.ds3_stats();

        let mut fsm = StateMachine::new(IDLE);
        fsm.add_state(StateDef { id: IDLE, name: "Idle".into(), duration: None, transitions: vec![Transition { target: ALERT, condition: target_close, priority: 1 }] });
        fsm.add_state(StateDef { id: ALERT, name: "Alert".into(), duration: Some(0.5), transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }] });
        fsm.add_state(StateDef { id: CHASE, name: "Chase".into(), duration: None, transitions: vec![
            Transition { target: ATTACK, condition: target_nearby, priority: 2 },
            Transition { target: RETURN, condition: target_far, priority: 1 },
        ] });
        fsm.add_state(StateDef { id: ATTACK, name: "Attack".into(), duration: Some(1.5), transitions: vec![Transition { target: CHASE, condition: attack_done, priority: 1 }] });
        fsm.add_state(StateDef { id: RETREAT, name: "Retreat".into(), duration: Some(1.0), transitions: vec![Transition { target: CHASE, condition: retreat_done, priority: 1 }] });
        fsm.add_state(StateDef { id: RETURN, name: "Return".into(), duration: None, transitions: vec![Transition { target: IDLE, condition: target_close, priority: 1 }] });
        fsm.add_state(StateDef { id: STAGGERED, name: "Staggered".into(), duration: Some(0.3), transitions: vec![Transition { target: CHASE, condition: always, priority: 1 }] });

        let aggro = AggroTable::new(260.0, 560.0);
        let behavior = kind.behavior_flags();
        Self {
            id, transform: Transform::new(x, y),
            hp, max_hp: hp, speed,
            state: EntityState::Idle, facing: 0.0,
            damage, attack_range,
            spawn_x: x, spawn_y: y, fsm, aggro,
            has_hit_this_attack: false, windup_timer: 0.0, parried_timer: 0.0, flash_timer: 0.0, death_timer: 0.0,
            kind,
            can_block: behavior.can_block, can_shoot: behavior.can_shoot, parryable_in_attack: behavior.parryable_in_attack,
            shoot_timer: if behavior.can_shoot { 1.5 } else { 0.0 },
            shoot_cooldown: 1.5,
            block_chance,
            patrol_timer: 0.0, patrol_dir: 1.0, patrol_range: 26.0,
            dodge_timer: 0.0, dodge_dir: 1.0,
            teleport_timer: 0.0,
            mimic_activated: false, grab_timer: 0.0,
        }
    }

    pub fn current_attack_can_be_parried(&self) -> bool {
        if !self.parryable_in_attack { return false; }
        match self.kind {
            EnemyKind::Archer | EnemyKind::DarkMage => self.fsm.current_state == ATTACK,
            EnemyKind::CrystalLizard => self.fsm.current_state == ATTACK,
            EnemyKind::Assassin => matches!(self.fsm.current_state, ATTACK | RANGED_ATTACK),
            _ => self.fsm.current_state == ATTACK,
        }
    }

    pub fn should_shoot(&mut self, dt: f32) -> bool {
        if !self.can_shoot { return false; }
        self.shoot_timer -= dt;
        if self.shoot_timer <= 0.0 {
            self.shoot_timer = self.shoot_cooldown;
            return true;
        }
        false
    }

    pub fn try_block(&self) -> bool {
        if !self.can_block { return false; }
        let r = (self.id.wrapping_mul(1103515245).wrapping_add(12345)) as f32;
        r % 100.0 < self.block_chance * 100.0
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
                            self.dodge_timer = 2.0 + ((self.id as f32 * 0.7).sin().abs() * 1.5);
                            self.dodge_dir = if (self.id as f32) % 2.0 < 1.0 { -1.0 } else { 1.0 };
                            let perp = self.facing + std::f32::consts::FRAC_PI_2 * self.dodge_dir;
                            let new_x = self.transform.x + perp.cos() * 48.0;
                            let new_y = self.transform.y + perp.sin() * 48.0;
                            let cell = nav_grid.world_to_cell(new_x - chunk_offset.0, new_y - chunk_offset.1);
                            if nav_grid.is_walkable(cell.x, cell.y) {
                                self.transform.x = new_x;
                                self.transform.y = new_y;
                            }
                        }
                    }

                    // Dark Mage: teleport when low HP
                    if self.kind == EnemyKind::DarkMage {
                        self.teleport_timer -= dt;
                        if self.teleport_timer <= 0.0 && self.hp < self.max_hp * 2 / 3 {
                            self.teleport_timer = 6.0;
                            let base_angle = (self.id as f32 * 1.7) % std::f32::consts::TAU;
                            let mut teleported = false;
                            // Try several angles to find a walkable target
                            for attempt in 0..8 {
                                let angle = base_angle + attempt as f32 * std::f32::consts::FRAC_PI_4;
                                let dist = 80.0;
                                let tx = self.spawn_x + angle.cos() * dist;
                                let ty = self.spawn_y + angle.sin() * dist;
                                let cell = nav_grid.world_to_cell(tx - chunk_offset.0, ty - chunk_offset.1);
                                if nav_grid.is_walkable(cell.x, cell.y) {
                                    self.transform.x = tx;
                                    self.transform.y = ty;
                                    self.flash_timer = 0.3;
                                    teleported = true;
                                    break;
                                }
                            }
                            if !teleported {
                                // Fallback: small step backward
                                let back = self.facing + std::f32::consts::PI;
                                let tx = self.transform.x + back.cos() * 24.0;
                                let ty = self.transform.y + back.sin() * 24.0;
                                let cell = nav_grid.world_to_cell(tx - chunk_offset.0, ty - chunk_offset.1);
                                if nav_grid.is_walkable(cell.x, cell.y) {
                                    self.transform.x = tx;
                                    self.transform.y = ty;
                                    self.flash_timer = 0.3;
                                }
                            }
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
                if self.kind == EnemyKind::CrystalLizard {
                    if self.state != EntityState::Attacking {
                        self.has_hit_this_attack = false;
                        self.windup_timer = 0.34;
                    }
                    self.attack_range = 66.0;
                    self.damage = 42;
                    if self.aggro.has_target() {
                        let dx = self.aggro.last_known_x - self.transform.x;
                        let dy = self.aggro.last_known_y - self.transform.y;
                        self.facing = dy.atan2(dx);
                        self.transform.scale_x = if self.facing.cos() < 0.0 { -1.0 } else { 1.0 };
                    }
                } else if self.state != EntityState::Attacking {
                    self.has_hit_this_attack = false;
                    self.windup_timer = 0.5; // Telegraph before hit
                }
                self.state = EntityState::Attacking;
            }
            RANGED_ATTACK => {
                if self.kind == EnemyKind::CrystalLizard {
                    if self.state != EntityState::Attacking {
                        self.has_hit_this_attack = false;
                        self.windup_timer = 0.18;
                    }
                    self.attack_range = 48.0;
                    self.damage = 48;
                    if self.aggro.has_target() {
                        let dx = self.aggro.last_known_x - self.transform.x;
                        let dy = self.aggro.last_known_y - self.transform.y;
                        self.facing = dy.atan2(dx);
                        let roll_speed = if self.windup_timer > 0.0 { self.speed * 0.55 } else { self.speed * 2.65 };
                        self.transform.x += self.facing.cos() * roll_speed * dt;
                        self.transform.y += self.facing.sin() * roll_speed * dt;
                        self.transform.scale_x = if self.facing.cos() < 0.0 { -1.0 } else { 1.0 };
                    }
                    self.transform.rotation += dt * 12.0 * self.transform.scale_x.signum();
                } else {
                    if self.aggro.has_target() {
                        let dx = self.aggro.last_known_x - self.transform.x;
                        let dy = self.aggro.last_known_y - self.transform.y;
                        self.facing = dy.atan2(dx);
                    }
                }
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
        if self.death_timer <= 0.0 && self.is_dead() {
            return;
        }
        if self.kind == EnemyKind::CrystalLizard {
            let alpha = if self.state == EntityState::Dead { (self.death_timer / 1.0).max(0.0) } else { 1.0 };
            let rolling = self.fsm.current_state == RANGED_ATTACK;
            let tail_sweep = self.fsm.current_state == ATTACK && self.state == EntityState::Attacking;
            let flash = self.flash_timer > 0.0;
            let base = if flash { [1.0, 1.0, 1.0, alpha] } else if self.state == EntityState::Staggered { [0.95, 0.95, 1.0, alpha] } else { [0.36, 0.86, 1.0, alpha] };
            let highlight = if flash { [1.0, 1.0, 1.0, alpha] } else { [0.82, 0.98, 1.0, alpha] };
            let shadow = if flash { [1.0, 1.0, 1.0, alpha] } else { [0.12, 0.38, 0.56, alpha] };
            let cx = self.transform.x;
            let cy = self.transform.y;
            let facing = self.facing;
            let fx = facing.cos();
            let fy = facing.sin();
            let sx = -fy;
            let sy = fx;

            if rolling {
                let rot = self.transform.rotation;
                Self::draw_part(batcher, texture, gl, cx - fx * 22.0, cy - fy * 22.0, 22.0, 12.0, facing, [0.25, 0.75, 1.0, alpha * 0.35]);
                Self::draw_part(batcher, texture, gl, cx, cy, 34.0, 34.0, rot, base);
                Self::draw_part(batcher, texture, gl, cx, cy, 38.0, 9.0, rot + 0.75, highlight);
                Self::draw_part(batcher, texture, gl, cx, cy, 38.0, 7.0, rot - 0.75, shadow);
                Self::draw_part(batcher, texture, gl, cx + fx * 4.0, cy + fy * 4.0, 12.0, 12.0, rot, [0.92, 1.0, 1.0, alpha]);
            } else {
                Self::draw_part(batcher, texture, gl, cx - fx * 19.0, cy - fy * 19.0, 34.0, 8.0, facing, shadow);
                Self::draw_part(batcher, texture, gl, cx, cy, 42.0, 24.0, facing, base);
                Self::draw_part(batcher, texture, gl, cx + fx * 24.0, cy + fy * 24.0, 18.0, 16.0, facing, highlight);
                Self::draw_part(batcher, texture, gl, cx - fx * 14.0 + sx * 8.0, cy - fy * 14.0 + sy * 8.0, 10.0, 18.0, facing - 0.9, highlight);
                Self::draw_part(batcher, texture, gl, cx - fx * 2.0 - sx * 10.0, cy - fy * 2.0 - sy * 10.0, 9.0, 20.0, facing + 0.9, highlight);
                Self::draw_part(batcher, texture, gl, cx + fx * 10.0 + sx * 8.0, cy + fy * 10.0 + sy * 8.0, 8.0, 16.0, facing - 0.7, [0.7, 0.95, 1.0, alpha]);
                Self::draw_part(batcher, texture, gl, cx - fx * 4.0, cy - fy * 4.0, 28.0, 6.0, facing, [0.96, 1.0, 1.0, alpha]);
            }

            if tail_sweep {
                let sweep_alpha = if self.windup_timer > 0.0 { 0.28 } else { 0.56 };
                let side = if self.transform.scale_x < 0.0 { -1.0 } else { 1.0 };
                let sweep_angle = facing + std::f32::consts::FRAC_PI_2 * side;
                Self::draw_part(batcher, texture, gl, cx - fx * 22.0 + sx * side * 24.0, cy - fy * 22.0 + sy * side * 24.0, 72.0, 8.0, sweep_angle, [0.82, 0.98, 1.0, alpha * sweep_alpha]);
                Self::draw_part(batcher, texture, gl, cx - fx * 28.0 + sx * side * 42.0, cy - fy * 28.0 + sy * side * 42.0, 36.0, 6.0, sweep_angle + 0.35 * side, [0.5, 0.9, 1.0, alpha * sweep_alpha]);
            }

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
                    let instance = self.transform.to_instance_data(28.0, 24.0, [0.0, 0.0, 1.0, 1.0], [0.8, 0.7, 0.2, 1.0]);
                    batcher.draw(instance, texture, gl);
                    return;
                }
                (38.0, [0.6, 0.4, 0.1, 1.0])
            },
            EnemyKind::CrystalLizard => (30.0, [0.36, 0.86, 1.0, 1.0]),
            // DS3-specific
            EnemyKind::SilverKnight => (34.0, [0.75, 0.75, 0.8, 1.0]),
            EnemyKind::BlackKnight => (36.0, [0.15, 0.15, 0.2, 1.0]),
            EnemyKind::DeepAccursed => (42.0, [0.3, 0.1, 0.4, 1.0]),
            EnemyKind::Evangelist => (32.0, [0.4, 0.35, 0.3, 1.0]),
            EnemyKind::Thrall => (18.0, [0.3, 0.25, 0.2, 1.0]),
            EnemyKind::LothricKnight => (34.0, [0.5, 0.5, 0.6, 1.0]),
            EnemyKind::WingedKnight => (38.0, [0.4, 0.4, 0.45, 1.0]),
            EnemyKind::Ghru => (28.0, [0.5, 0.35, 0.2, 1.0]),
            EnemyKind::Darkwraith => (34.0, [0.1, 0.1, 0.15, 1.0]),
            EnemyKind::Skeleton => (26.0, [0.85, 0.85, 0.75, 1.0]),
            EnemyKind::Jailer => (32.0, [0.2, 0.15, 0.2, 1.0]),
            EnemyKind::SerpentMan => (32.0, [0.6, 0.5, 0.3, 1.0]),
            EnemyKind::Deacon => (26.0, [0.5, 0.3, 0.2, 1.0]),
            EnemyKind::FireDemon => (40.0, [0.7, 0.25, 0.1, 1.0]),
            EnemyKind::StarvedHound => (20.0, [0.5, 0.4, 0.3, 1.0]),
            EnemyKind::PusOfMan => (36.0, [0.1, 0.05, 0.15, 1.0]),
            EnemyKind::CathedralKnight => (36.0, [0.4, 0.4, 0.35, 1.0]),
            EnemyKind::ManGrub => (24.0, [0.6, 0.5, 0.3, 1.0]),
            EnemyKind::Gargoyle => (36.0, [0.45, 0.45, 0.4, 1.0]),
            EnemyKind::Dog => (18.0, [0.5, 0.35, 0.25, 1.0]),
            EnemyKind::Basilisk => (22.0, [0.4, 0.6, 0.3, 1.0]),
            EnemyKind::DemonStatue => (30.0, [0.6, 0.3, 0.2, 1.0]),
            EnemyKind::InfestedCorpse => (26.0, [0.4, 0.35, 0.3, 1.0]),
            EnemyKind::Wretch => (26.0, [0.3, 0.25, 0.2, 1.0]),
            EnemyKind::PeasantHollow => (24.0, [0.55, 0.5, 0.45, 1.0]),
            EnemyKind::GiantSlave => (48.0, [0.5, 0.4, 0.3, 1.0]),
            EnemyKind::HollowAssassin => (22.0, [0.3, 0.3, 0.35, 1.0]),
            EnemyKind::CathedralGraveWarden => (30.0, [0.3, 0.35, 0.3, 1.0]),
            EnemyKind::Rat => (14.0, [0.45, 0.35, 0.25, 1.0]),
            EnemyKind::LargeHollowSoldier => (36.0, [0.55, 0.5, 0.45, 1.0]),
            EnemyKind::MiniBoss => (40.0, [0.7, 0.3, 0.2, 1.0]),
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

    fn take_damage(&mut self, info: &DamageInfo) -> DamageOutcome {
        self.hp -= info.damage;
        self.flash_timer = 0.12;
        self.aggro.add_threat(info.damage as f32 * 2.0);
        self.fsm.current_state = STAGGERED;
        self.fsm.state_timer = 0.0;
        self.state = EntityState::Staggered;
        let killed = self.hp <= 0;
        if killed {
            self.hp = 0;
            self.fsm.current_state = DEAD;
            self.state = EntityState::Dead;
            self.death_timer = 1.0;
        }
        DamageOutcome::applied(info.damage, info.damage, killed)
    }

    fn is_dead(&self) -> bool {
        self.hp <= 0
    }
}
