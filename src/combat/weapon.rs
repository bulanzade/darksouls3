use crate::combat::moveset::{LongswordMoveset, WeaponMoveset};
use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub enum WeaponType {
    Longsword,
    GreatAxe,
    Dagger,
    Spear,
    Uchigatana,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Weapon {
    pub name: String,
    pub weapon_type: WeaponType,
    pub base_damage: i32,
    pub strength_requirement: u32,
    pub dexterity_requirement: u32,
    pub strength_scaling: f32,
    pub dexterity_scaling: f32,
    pub weight: f32,
    pub stability: f32,
    pub crit_modifier: f32,
}

impl Weapon {
    pub fn longsword() -> Self {
        Self {
            name: "Longsword".into(),
            weapon_type: WeaponType::Longsword,
            base_damage: 80,
            strength_requirement: 10,
            dexterity_requirement: 8,
            strength_scaling: 0.6,
            dexterity_scaling: 0.6,
            weight: 3.0,
            stability: 0.0,
            crit_modifier: 1.0,
        }
    }

    pub fn great_axe() -> Self {
        Self {
            name: "Great Axe".into(),
            weapon_type: WeaponType::GreatAxe,
            base_damage: 130,
            strength_requirement: 18,
            dexterity_requirement: 5,
            strength_scaling: 1.0,
            dexterity_scaling: 0.2,
            weight: 8.0,
            stability: 0.0,
            crit_modifier: 0.8,
        }
    }

    pub fn dagger() -> Self {
        Self {
            name: "Dagger".into(),
            weapon_type: WeaponType::Dagger,
            base_damage: 45,
            strength_requirement: 3,
            dexterity_requirement: 12,
            strength_scaling: 0.3,
            dexterity_scaling: 1.0,
            weight: 1.0,
            stability: 0.0,
            crit_modifier: 2.0,
        }
    }

    pub fn spear() -> Self {
        Self {
            name: "Spear".into(),
            weapon_type: WeaponType::Spear,
            base_damage: 70,
            strength_requirement: 8,
            dexterity_requirement: 10,
            strength_scaling: 0.5,
            dexterity_scaling: 0.7,
            weight: 4.0,
            stability: 0.0,
            crit_modifier: 1.0,
        }
    }

    pub fn uchigatana() -> Self {
        Self {
            name: "Uchigatana".into(),
            weapon_type: WeaponType::Uchigatana,
            base_damage: 95,
            strength_requirement: 7,
            dexterity_requirement: 14,
            strength_scaling: 0.3,
            dexterity_scaling: 1.0,
            weight: 5.0,
            stability: 0.0,
            crit_modifier: 1.3,
        }
    }

    pub fn get_moveset(&self) -> Box<dyn WeaponMoveset> {
        match self.weapon_type {
            WeaponType::Longsword => Box::new(LongswordMoveset),
            _ => Box::new(LongswordMoveset),
        }
    }
}
