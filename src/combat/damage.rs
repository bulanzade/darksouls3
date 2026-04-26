/// Simplified DS2 damage calculation
pub fn calculate_damage(
    attack_rating: f32,
    defense: f32,
    counter_modifier: f32,
    buff_modifier: f32,
) -> i32 {
    let reduction = if attack_rating > defense * 8.0 {
        defense * 0.1
    } else if attack_rating > defense {
        attack_rating * (0.1 + (defense / attack_rating - 1.0) * 0.4)
    } else {
        attack_rating * (0.4 * attack_rating / defense)
    };

    let final_damage = (attack_rating - reduction) * counter_modifier * buff_modifier;
    final_damage.max(1.0) as i32
}

/// Calculate attack rating from weapon + stats
pub fn calculate_attack_rating(
    base_damage: i32,
    strength: u32,
    dexterity: u32,
    str_requirement: u32,
    dex_requirement: u32,
    str_scaling: f32,
    dex_scaling: f32,
) -> f32 {
    let meets_str = strength >= str_requirement;
    let meets_dex = dexterity >= dex_requirement;

    let str_bonus = if meets_str {
        let soft_cap = (strength as f32).min(40.0);
        soft_cap / 40.0 * str_scaling * base_damage as f32
    } else {
        -0.1 * base_damage as f32
    };

    let dex_bonus = if meets_dex {
        let soft_cap = (dexterity as f32).min(40.0);
        soft_cap / 40.0 * dex_scaling * base_damage as f32
    } else {
        -0.1 * base_damage as f32
    };

    base_damage as f32 + str_bonus + dex_bonus
}
