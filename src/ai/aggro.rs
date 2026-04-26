use crate::entity::entity_trait::EntityId;

#[derive(Clone, Debug)]
pub struct AggroTable {
    pub detection_radius: f32,
    pub deaggro_radius: f32,
    pub target_id: Option<EntityId>,
    pub threat: f32,
    pub can_see_target: bool,
    pub last_known_x: f32,
    pub last_known_y: f32,
}

impl AggroTable {
    pub fn new(detection_radius: f32, deaggro_radius: f32) -> Self {
        Self {
            detection_radius,
            deaggro_radius,
            target_id: None,
            threat: 0.0,
            can_see_target: false,
            last_known_x: 0.0,
            last_known_y: 0.0,
        }
    }

    pub fn check_detection(
        &mut self,
        my_x: f32,
        my_y: f32,
        target_id: EntityId,
        target_x: f32,
        target_y: f32,
    ) {
        let dx = target_x - my_x;
        let dy = target_y - my_y;
        let dist = (dx * dx + dy * dy).sqrt();

        if dist < self.detection_radius {
            self.target_id = Some(target_id);
            self.can_see_target = true;
            self.last_known_x = target_x;
            self.last_known_y = target_y;
        } else if dist > self.deaggro_radius {
            self.can_see_target = false;
        }

        if let Some(_id) = self.target_id {
            self.last_known_x = target_x;
            self.last_known_y = target_y;
        }
    }

    pub fn add_threat(&mut self, amount: f32) {
        self.threat += amount;
    }

    pub fn distance_to_target(&self, my_x: f32, my_y: f32) -> f32 {
        let dx = self.last_known_x - my_x;
        let dy = self.last_known_y - my_y;
        (dx * dx + dy * dy).sqrt()
    }

    pub fn has_target(&self) -> bool {
        self.target_id.is_some()
    }
}
