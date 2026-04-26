use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Equipment {
    pub right_hand_1: Option<String>,  // Weapon name
    pub right_hand_2: Option<String>,
    pub left_hand_1: Option<String>,   // Weapon or shield
    pub left_hand_2: Option<String>,
    pub head: Option<String>,
    pub chest: Option<String>,
    pub hands: Option<String>,
    pub legs: Option<String>,
    pub ring_1: Option<String>,
    pub ring_2: Option<String>,
    pub ring_3: Option<String>,
    pub ring_4: Option<String>,
}

impl Default for Equipment {
    fn default() -> Self {
        Self {
            right_hand_1: Some("Longsword".into()),
            right_hand_2: None,
            left_hand_1: None,
            left_hand_2: None,
            head: None,
            chest: None,
            hands: None,
            legs: None,
            ring_1: None, ring_2: None, ring_3: None, ring_4: None,
        }
    }
}

impl Equipment {
    pub fn total_weight(&self) -> f32 {
        // MVP: just return 3.0 (longsword weight)
        // Full impl would look up each item's weight
        3.0
    }

    pub fn total_defense(&self) -> f32 {
        50.0 // Base defense
    }

    pub fn is_two_handing(&self) -> bool {
        false // For now
    }
}
