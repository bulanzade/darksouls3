/// DS2 approximate soul cost to reach next level
pub fn soul_cost_to_level(current_level: u32) -> u32 {
    let level = current_level as f64;
    ((level - 1.0).powi(3) * 0.55 + level * 100.0) as u32
}

/// Cost table for first 20 levels (for testing)
pub fn soul_cost_table() -> Vec<u32> {
    (1..=20).map(|l| soul_cost_to_level(l)).collect()
}
