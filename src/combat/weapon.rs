use crate::combat::moveset::{LongswordMoveset, GreatAxeMoveset, DaggerMoveset, SpearMoveset, UchigatanaMoveset, WeaponMoveset};
use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub enum WeaponType {
    Longsword,
    GreatAxe,
    Dagger,
    Spear,
    Uchigatana,
    Shield,
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
            name: "直剑".into(),
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
            name: "大斧".into(),
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
            name: "匕首".into(),
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
            name: "长枪".into(),
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
            name: "打刀".into(),
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

    pub fn shield() -> Self {
        Self {
            name: "骑士盾".into(),
            weapon_type: WeaponType::Shield,
            base_damage: 20,
            strength_requirement: 10,
            dexterity_requirement: 5,
            strength_scaling: 0.3,
            dexterity_scaling: 0.1,
            weight: 3.5,
            stability: 0.6,
            crit_modifier: 0.5,
        }
    }

    pub fn get_moveset(&self) -> Box<dyn WeaponMoveset> {
        match self.weapon_type {
            WeaponType::Longsword => Box::new(LongswordMoveset),
            WeaponType::GreatAxe => Box::new(GreatAxeMoveset),
            WeaponType::Dagger => Box::new(DaggerMoveset),
            WeaponType::Spear => Box::new(SpearMoveset),
            WeaponType::Uchigatana => Box::new(UchigatanaMoveset),
            WeaponType::Shield => Box::new(LongswordMoveset), // Shield uses basic moveset
        }
    }
}
