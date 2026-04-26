use crate::combat::moveset::{LongswordMoveset, WeaponMoveset};

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum WeaponType {
    Longsword,
    GreatAxe,
    Dagger,
    Spear,
    Uchigatana,
}

#[derive(Clone, Debug)]
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

    pub fn get_moveset(&self) -> Box<dyn WeaponMoveset> {
        match self.weapon_type {
            WeaponType::Longsword => Box::new(LongswordMoveset),
            _ => Box::new(LongswordMoveset),
        }
    }
}
