use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CharacterStats {
    pub vigor: u32,        // Max HP
    pub endurance: u32,    // Max stamina
    pub vitality: u32,     // Max equip load
    pub strength: u32,     // STR weapon scaling
    pub dexterity: u32,    // DEX weapon scaling
    pub adaptability: u32, // Agility (iframes, item use speed)
    pub intelligence: u32, // Spell requirement + scaling
    pub faith: u32,        // Miracle requirement + scaling
    pub attunement: u32,   // Spell slots + minor AGI boost
    pub luck: u32,         // Item discovery, bleed/poison bonus
}

impl Default for CharacterStats {
    fn default() -> Self {
        Self {
            vigor: 10, endurance: 10, vitality: 10,
            strength: 10, dexterity: 10, adaptability: 5,
            intelligence: 5, faith: 5, attunement: 5, luck: 5,
        }
    }
}

impl CharacterStats {
    /// Derived max HP: 200 + vigor * 30, soft cap at 50
    pub fn max_hp(&self) -> i32 {
        let effective = (self.vigor as f32).min(50.0);
        (200.0 + effective * 30.0) as i32
    }

    /// Derived max stamina: 80 + endurance * 2, soft cap at 20
    pub fn max_stamina(&self) -> f32 {
        let effective = (self.endurance as f32).min(20.0);
        80.0 + effective * 2.0
    }

    /// Derived max equip load: 40 + vitality * 1.5
    pub fn max_equip_load(&self) -> f32 {
        40.0 + self.vitality as f32 * 1.5
    }

    /// Agility: 80 + adaptability * 3 + attunement * 0.5
    pub fn agility(&self) -> f32 {
        80.0 + self.adaptability as f32 * 3.0 + self.attunement as f32 * 0.5
    }

    /// Iframes from agility (DS2 breakpoints)
    pub fn iframe_count(&self) -> u32 {
        let agi = self.agility();
        if agi >= 110.0 { 15 }
        else if agi >= 105.0 { 13 }
        else if agi >= 99.0 { 11 }
        else if agi >= 96.0 { 9 }
        else if agi >= 92.0 { 8 }
        else { 5 }
    }

    /// Item discovery: 100 + luck * 2
    pub fn item_discovery(&self) -> u32 {
        100 + self.luck * 2
    }

    /// Total soul level (sum of all stats minus base 80)
    pub fn soul_level(&self) -> u32 {
        self.vigor + self.endurance + self.vitality +
        self.strength + self.dexterity + self.adaptability +
        self.intelligence + self.faith + self.attunement + self.luck
    }
}
