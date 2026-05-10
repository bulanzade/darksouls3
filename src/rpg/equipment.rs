use crate::combat::weapon::{Weapon, WeaponType};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ArmorPiece {
    pub name: String,
    pub defense: f32,
    pub weight: f32,
    pub poison_resist: f32,
}

impl ArmorPiece {
    pub fn none() -> Self {
        Self { name: "None".into(), defense: 0.0, weight: 0.0, poison_resist: 0.0 }
    }
    pub fn hollow_soldier_helm() -> Self {
        Self { name: "Hollow Soldier Helm".into(), defense: 5.0, weight: 2.0, poison_resist: 0.0 }
    }
    pub fn hollow_soldier_chest() -> Self {
        Self { name: "Hollow Soldier Armor".into(), defense: 12.0, weight: 5.0, poison_resist: 2.0 }
    }
    pub fn knight_helm() -> Self {
        Self { name: "Knight Helm".into(), defense: 8.0, weight: 3.0, poison_resist: 0.0 }
    }
    pub fn knight_chest() -> Self {
        Self { name: "Knight Armor".into(), defense: 18.0, weight: 8.0, poison_resist: 5.0 }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Ring {
    pub name: String,
    pub effect: RingEffect,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum RingEffect {
    HpBonus(f32),
    StaminaRegen(f32),
    DamageBonus(f32),
    SoulBonus(f32),
    PoisonResist(f32),
}

impl Ring {
    pub fn none() -> Self {
        Self { name: "None".into(), effect: RingEffect::HpBonus(0.0) }
    }
    pub fn life_ring() -> Self {
        Self { name: "Life Ring".into(), effect: RingEffect::HpBonus(0.1) }
    }
    pub fn chloranthy() -> Self {
        Self { name: "Chloranthy Ring".into(), effect: RingEffect::StaminaRegen(0.3) }
    }
    pub fn lion_ring() -> Self {
        Self { name: "Ring of the Lion".into(), effect: RingEffect::DamageBonus(0.15) }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Equipment {
    pub right_hand: WeaponSlot,
    pub left_hand: WeaponSlot,
    pub head: ArmorPiece,
    pub chest: ArmorPiece,
    pub legs: ArmorPiece,
    pub hands: ArmorPiece,
    pub ring_1: Option<Ring>,
    pub ring_2: Option<Ring>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct WeaponSlot {
    pub primary: Weapon,
    pub secondary: Option<Weapon>,
    pub using_primary: bool,
}

impl WeaponSlot {
    pub fn new(weapon: Weapon) -> Self {
        Self { primary: weapon, secondary: None, using_primary: true }
    }

    pub fn fist() -> Self {
        Self { primary: Weapon::fist(), secondary: None, using_primary: true }
    }

    pub fn active(&self) -> &Weapon {
        if self.using_primary { &self.primary } else { self.secondary.as_ref().unwrap_or(&self.primary) }
    }

    pub fn swap(&mut self) {
        if self.secondary.is_some() {
            self.using_primary = !self.using_primary;
        } else if self.primary.weapon_type != WeaponType::Fist {
            let old = std::mem::replace(&mut self.primary, Weapon::fist());
            self.secondary = Some(old);
            self.using_primary = true;
        }
    }
}

impl Default for Equipment {
    fn default() -> Self {
        Self {
            right_hand: WeaponSlot::fist(),
            left_hand: WeaponSlot::fist(),
            head: ArmorPiece::none(),
            chest: ArmorPiece::none(),
            legs: ArmorPiece::none(),
            hands: ArmorPiece::none(),
            ring_1: None,
            ring_2: None,
        }
    }
}

impl Equipment {
    pub fn total_weight(&self) -> f32 {
        let weapon_w = self.right_hand.active().weight;
        let armor_w = self.head.weight + self.chest.weight + self.legs.weight + self.hands.weight;
        weapon_w + armor_w
    }

    pub fn total_defense(&self) -> f32 {
        self.head.defense + self.chest.defense + self.legs.defense + self.hands.defense
    }

    pub fn poison_resist(&self) -> f32 {
        let base = self.head.poison_resist + self.chest.poison_resist + self.legs.poison_resist + self.hands.poison_resist;
        let ring_bonus: f32 = [&self.ring_1, &self.ring_2].iter()
            .filter_map(|r| r.as_ref())
            .map(|r| match &r.effect {
                RingEffect::PoisonResist(v) => *v,
                _ => 0.0,
            })
            .sum();
        (base + ring_bonus) / 100.0
    }

    pub fn hp_bonus(&self) -> f32 {
        [&self.ring_1, &self.ring_2].iter()
            .filter_map(|r| r.as_ref())
            .map(|r| match &r.effect {
                RingEffect::HpBonus(v) => *v,
                _ => 0.0,
            })
            .sum()
    }

    pub fn stamina_regen_bonus(&self) -> f32 {
        [&self.ring_1, &self.ring_2].iter()
            .filter_map(|r| r.as_ref())
            .map(|r| match &r.effect {
                RingEffect::StaminaRegen(v) => *v,
                _ => 0.0,
            })
            .sum()
    }

    pub fn damage_bonus(&self) -> f32 {
        [&self.ring_1, &self.ring_2].iter()
            .filter_map(|r| r.as_ref())
            .map(|r| match &r.effect {
                RingEffect::DamageBonus(v) => *v,
                _ => 0.0,
            })
            .sum()
    }

    pub fn soul_bonus(&self) -> f32 {
        [&self.ring_1, &self.ring_2].iter()
            .filter_map(|r| r.as_ref())
            .map(|r| match &r.effect {
                RingEffect::SoulBonus(v) => *v,
                _ => 0.0,
            })
            .sum()
    }

    /// Equip load percentage: weight / max_load
    /// <30% = fast roll, 30-70% = medium, 70-100% = fat roll
    pub fn equip_load_percent(&self, max_load: f32) -> f32 {
        if max_load <= 0.0 { return 1.0; }
        self.total_weight() / max_load
    }
}
