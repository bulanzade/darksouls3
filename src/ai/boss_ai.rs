#[derive(Clone, Debug)]
pub struct BossPhase {
    pub health_threshold: f32, // Activate at or below this fraction (0.0-1.0)
    pub speed_multiplier: f32,
    pub damage_multiplier: f32,
    pub attack_cooldown: f32, // Seconds between attacks
    pub new_attack_damage: i32,
    pub phase_name: String,
}

pub struct BossController {
    pub phases: Vec<BossPhase>,
    pub current_phase: usize,
    pub cooldown_timer: f32,
    pub is_transitioning: bool,
    pub transition_timer: f32,
    pub transition_duration: f32,
}

impl BossController {
    pub fn new(phases: Vec<BossPhase>) -> Self {
        Self {
            phases,
            current_phase: 0,
            cooldown_timer: 0.0,
            is_transitioning: false,
            transition_timer: 0.0,
            transition_duration: 1.5,
        }
    }

    pub fn update(&mut self, hp_ratio: f32, dt: f32) -> BossDirective {
        if self.is_transitioning {
            self.transition_timer -= dt;
            if self.transition_timer <= 0.0 {
                self.is_transitioning = false;
                self.cooldown_timer = self.phases[self.current_phase].attack_cooldown;
            }
            return BossDirective::PhaseTransition;
        }

        // Check for phase transition
        for (i, phase) in self.phases.iter().enumerate() {
            if i > self.current_phase && hp_ratio <= phase.health_threshold {
                self.current_phase = i;
                self.is_transitioning = true;
                self.transition_timer = self.transition_duration;
                return BossDirective::PhaseTransition;
            }
        }

        self.cooldown_timer -= dt;

        let phase = &self.phases[self.current_phase];
        if self.cooldown_timer <= 0.0 {
            self.cooldown_timer = phase.attack_cooldown;
            BossDirective::Attack
        } else {
            BossDirective::Chase
        }
    }

    pub fn current_phase(&self) -> &BossPhase {
        &self.phases[self.current_phase]
    }

    pub fn current_phase_index(&self) -> usize {
        self.current_phase
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum BossDirective {
    Chase,
    Attack,
    PhaseTransition,
}
