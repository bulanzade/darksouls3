use std::collections::HashMap;

pub type StateId = u8;

pub struct StateMachine {
    pub current_state: StateId,
    states: HashMap<StateId, StateDef>,
    pub state_timer: f32,
}

pub struct StateDef {
    pub id: StateId,
    pub name: String,
    pub duration: Option<f32>, // None = indefinite
    pub transitions: Vec<Transition>,
}

pub struct Transition {
    pub target: StateId,
    pub condition: fn(&TransitionContext) -> bool,
    pub priority: i32, // Higher = checked first
}

pub struct TransitionContext {
    pub distance_to_target: f32,
    pub hp_ratio: f32,
    pub stamina_ratio: f32,
    pub state_timer: f32,
    pub can_see_target: bool,
}

impl StateMachine {
    pub fn new(initial_state: StateId) -> Self {
        Self {
            current_state: initial_state,
            states: HashMap::new(),
            state_timer: 0.0,
        }
    }

    pub fn add_state(&mut self, def: StateDef) {
        self.states.insert(def.id, def);
    }

    pub fn update(&mut self, dt: f32, ctx: &TransitionContext) -> StateId {
        self.state_timer += dt;

        // Check duration-based transition
        if let Some(state) = self.states.get(&self.current_state) {
            if let Some(dur) = state.duration {
                if self.state_timer >= dur {
                    // Find default transition (lowest priority or first)
                    if let Some(trans) = state.transitions.first() {
                        self.transition(trans.target);
                        return self.current_state;
                    }
                }
            }
        }

        // Check condition-based transitions (sorted by priority desc)
        if let Some(state) = self.states.get(&self.current_state) {
            let mut transitions: Vec<&Transition> = state.transitions.iter().collect();
            transitions.sort_by(|a, b| b.priority.cmp(&a.priority));

            for trans in transitions {
                if (trans.condition)(ctx) {
                    self.transition(trans.target);
                    return self.current_state;
                }
            }
        }

        self.current_state
    }

    fn transition(&mut self, target: StateId) {
        self.current_state = target;
        self.state_timer = 0.0;
    }

    pub fn in_state(&self, id: StateId) -> bool {
        self.current_state == id
    }
}

// Common state IDs
pub const IDLE: StateId = 0;
pub const ALERT: StateId = 1;
pub const CHASE: StateId = 2;
pub const ATTACK: StateId = 3;
pub const RETREAT: StateId = 4;
pub const RETURN: StateId = 5;
pub const STAGGERED: StateId = 6;
pub const DEAD: StateId = 7;

// Helper transition conditions
pub fn always(_: &TransitionContext) -> bool {
    true
}
pub fn target_close(ctx: &TransitionContext) -> bool {
    ctx.distance_to_target < 200.0
}
pub fn target_nearby(ctx: &TransitionContext) -> bool {
    ctx.distance_to_target < 40.0
}
pub fn target_far(ctx: &TransitionContext) -> bool {
    ctx.distance_to_target > 300.0 || !ctx.can_see_target
}
pub fn low_hp(ctx: &TransitionContext) -> bool {
    ctx.hp_ratio < 0.3
}
pub fn attack_done(ctx: &TransitionContext) -> bool {
    ctx.state_timer > 1.2
}
pub fn retreat_done(ctx: &TransitionContext) -> bool {
    ctx.state_timer > 1.0
}
