/// Convert scaling letter grade to multiplier curve value
pub fn scaling_grade_to_multiplier(grade: ScalingGrade, stat_value: u32) -> f32 {
    let base = match grade {
        ScalingGrade::S => 1.5,
        ScalingGrade::A => 1.2,
        ScalingGrade::B => 0.9,
        ScalingGrade::C => 0.6,
        ScalingGrade::D => 0.35,
        ScalingGrade::E => 0.15,
        ScalingGrade::None => 0.0,
    };

    let soft_capped = (stat_value as f32).min(40.0) / 40.0;
    let diminishing = if stat_value > 40 {
        1.0 + (stat_value - 40) as f32 * 0.02
    } else {
        1.0
    };

    base * soft_capped * diminishing
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum ScalingGrade {
    S,
    A,
    B,
    C,
    D,
    E,
    None,
}

impl ScalingGrade {
    pub fn from_multiplier(m: f32) -> Self {
        if m >= 1.4 { Self::S }
        else if m >= 1.0 { Self::A }
        else if m >= 0.75 { Self::B }
        else if m >= 0.45 { Self::C }
        else if m >= 0.25 { Self::D }
        else if m > 0.0 { Self::E }
        else { Self::None }
    }
}
