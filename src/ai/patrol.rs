#[derive(Clone, Debug)]
pub struct PatrolPath {
    pub waypoints: Vec<(f32, f32)>,
    pub current_index: usize,
    pub loop_patrol: bool,
}

impl PatrolPath {
    pub fn new(waypoints: Vec<(f32, f32)>) -> Self {
        Self { waypoints, current_index: 0, loop_patrol: true }
    }

    pub fn current_target(&self) -> Option<(f32, f32)> {
        self.waypoints.get(self.current_index).copied()
    }

    pub fn update(&mut self, position: (f32, f32), arrival_distance: f32) -> bool {
        if let Some(target) = self.current_target() {
            let dx = target.0 - position.0;
            let dy = target.1 - position.1;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < arrival_distance {
                self.advance();
                return true;
            }
        }
        false
    }

    pub fn advance(&mut self) {
        if self.waypoints.is_empty() { return; }
        self.current_index += 1;
        if self.current_index >= self.waypoints.len() {
            if self.loop_patrol {
                self.current_index = 0;
            } else {
                self.current_index = self.waypoints.len() - 1;
            }
        }
    }

    pub fn direction_to_next(&self, from: (f32, f32)) -> (f32, f32) {
        if let Some(target) = self.current_target() {
            let dx = target.0 - from.0;
            let dy = target.1 - from.1;
            let len = (dx * dx + dy * dy).sqrt();
            if len > 0.0 { (dx / len, dy / len) } else { (0.0, 0.0) }
        } else {
            (0.0, 0.0)
        }
    }
}
