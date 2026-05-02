use crate::ai::state_machine::STAGGERED;
use crate::bridge::wasm_entry::{
    area_boss, fill_tiles, rebuild_collision, AreaId, BlockSpark, DamageNumber,
    DeathParticle, Game, ScreenFlash, SoulOrb,
};
use crate::entity::boss::BossType;
use crate::entity::entity_trait::{AttackTarget, DamageInfo, Entity, EntityState};
use crate::world::tileset::TileId;

pub(crate) fn tick_combat(game: &mut Game) {
    let (px, py) = game.player.position();
    let player_attacking = *game.player.state() == EntityState::Attacking && game.player.attack_timer > 0.0;
    let is_heavy = game.player.is_heavy_attack;
    let attack_range = if is_heavy { 56.0 } else { 40.0 };
    let attack_damage = if is_heavy { game.player.damage() * 2 } else { game.player.damage() };

    // --- Player vs enemies ---
    for enemy in &mut game.enemies {
        if enemy.is_dead() {
            continue;
        }
        let (ex, ey) = enemy.position();
        let dist = ((px - ex) * (px - ex) + (py - ey) * (py - ey)).sqrt();

        if player_attacking && dist < attack_range {
            let target = AttackTarget::Enemy(enemy.id());
            if !game.player.attack_tracker.has_hit(target) {
                game.player.attack_tracker.mark_hit(target);

                let blocked = enemy.try_block();
                let final_damage = if blocked { (attack_damage as f32 * 0.3) as i32 } else { attack_damage };
                let is_riposte = game.riposte_timer > 0.0 && game.riposte_target_id == enemy.id();
                let riposte_multiplier = if is_riposte { 3.0 } else { 1.0 };
                let actual_damage = (final_damage as f32 * riposte_multiplier) as i32;
                let dmg = DamageInfo {
                    damage: actual_damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: if is_heavy { 40.0 } else { 20.0 },
                    attacker_id: game.player.id(),
                    parryable: false,
                };
                let outcome = enemy.take_damage(&dmg);
                if !outcome.was_ignored {
                    game.camera.add_shake(if is_riposte { 10.0 } else if is_heavy { 6.0 } else { 3.0 });
                    game.hitstop_timer = if is_heavy { 0.05 } else { 0.02 };
                    game.audio.play_sfx("hit", if is_riposte { 0.2 } else { 0.12 }, 0.0);
                    game.damage_numbers.push(DamageNumber {
                        x: ex + ((game.damage_numbers.len() as f32 % 5.0) - 2.0) * 4.0,
                        y: ey - 24.0,
                        vy: -40.0,
                        value: outcome.actual_damage,
                        timer: 0.8,
                        is_player_damage: false,
                    });
                    game.damage_dealt += outcome.actual_damage as u32;
                    if blocked {
                        game.block_sparks.push(BlockSpark { x: ex, y: ey, timer: 0.3 });
                    } else {
                        game.stagger_bursts.push(BlockSpark { x: ex, y: ey, timer: 0.2 });
                    }
                }
                if is_riposte {
                    game.riposte_timer = 0.0;
                    game.riposte_target_id = 0;
                    game.screen_flash = Some(ScreenFlash { timer: 0.15, max_timer: 0.15, color: [1.0, 0.9, 0.3, 0.3] });
                }
                if outcome.killed {
                    game.enemies_killed += 1;
                    let soul_reward = match enemy.kind {
                        crate::entity::enemy::EnemyKind::HollowSoldier => 100,
                        crate::entity::enemy::EnemyKind::Archer => 150,
                        crate::entity::enemy::EnemyKind::Knight => 200,
                        crate::entity::enemy::EnemyKind::Assassin => 250,
                        crate::entity::enemy::EnemyKind::DarkMage => 300,
                        crate::entity::enemy::EnemyKind::Mimic => 500,
                        crate::entity::enemy::EnemyKind::CrystalLizard => 1200,
                    };
                    let soul_bonus = game.player.equipment.soul_bonus();
                    game.souls += (soul_reward as f32 * (1.0 + soul_bonus)) as u32;
                    game.camera.add_shake(6.0);
                    game.audio.play_sfx("enemy_die", 0.1, 0.0);
                    for i in 0..12 {
                        let angle = (i as f32 / 12.0) * std::f32::consts::TAU;
                        let speed = 40.0 + (i as f32 % 4.0) * 15.0;
                        game.death_particles.push(DeathParticle {
                            x: ex + (i as f32 % 3.0 - 1.0) * 6.0,
                            y: ey + (i as f32 % 3.0 - 1.0) * 6.0,
                            vx: angle.cos() * speed,
                            vy: -(angle.sin() * speed) + 30.0,
                            timer: 0.4 + (i as f32 % 4.0) * 0.1,
                            size: 4.0 + (i as f32 % 3.0) * 2.0,
                        });
                    }
                    for _ in 0..5 {
                        // len() grows per orb, giving deterministic visual spread
                        let idx = game.soul_orbs.len() as f32;
                        game.soul_orbs.push(SoulOrb {
                            x: ex + (idx % 3.0 - 1.0) * 6.0,
                            y: ey,
                            vy: -(30.0 + (idx % 5.0) * 8.0),
                            timer: 0.6 + (idx % 3.0) * 0.2,
                            max_time: 0.6 + (idx % 3.0) * 0.2,
                        });
                    }
                }
            }
        }

        if *enemy.state() == EntityState::Attacking && enemy.windup_timer <= 0.0 && dist < enemy.attack_range && !enemy.has_hit_this_attack {
            if *game.player.state() != EntityState::Rolling {
                let dmg = DamageInfo {
                    damage: enemy.damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: 10.0,
                    attacker_id: enemy.id(),
                    parryable: enemy.current_attack_can_be_parried(),
                };
                let outcome = game.player.take_damage(&dmg);

                if outcome.was_parried {
                    enemy.fsm.current_state = STAGGERED;
                    enemy.fsm.state_timer = 0.0;
                    enemy.state = EntityState::Staggered;
                    enemy.parried_timer = 2.0;
                    enemy.has_hit_this_attack = true;
                    game.riposte_timer = 2.0;
                    game.riposte_target_id = enemy.id();
                    game.screen_flash = Some(ScreenFlash { timer: 0.12, max_timer: 0.12, color: [0.2, 1.0, 1.0, 0.4] });
                    game.stagger_bursts.push(BlockSpark { x: (px + ex) * 0.5, y: (py + ey) * 0.5, timer: 0.3 });
                    game.audio.play_sfx("hit", 0.15, 0.0);
                } else if outcome.was_blocked {
                    game.damage_taken += outcome.actual_damage as u32;
                    game.audio.play_sfx("hit", 0.08, 0.0);
                } else if outcome.actual_damage > 0 {
                    game.camera.add_shake(8.0);
                    game.audio.play_sfx("player_hit", 0.15, 0.0);
                    game.damage_taken += outcome.actual_damage as u32;
                    game.damage_numbers.push(DamageNumber {
                        x: px,
                        y: py - 24.0,
                        vy: -50.0,
                        value: outcome.actual_damage,
                        timer: 0.8,
                        is_player_damage: true,
                    });
                }
                enemy.has_hit_this_attack = true;
            }
        }
    }

    // --- Player vs boss ---
    let mut gundyr_door = false;
    if let Some(ref mut boss) = game.boss {
        let (bx, by) = boss.position();
        let dist = ((px - bx) * (px - bx) + (py - by) * (py - by)).sqrt();

        if player_attacking && dist < attack_range + 16.0 && game.boss_intro_timer <= 0.0 {
            let target = AttackTarget::Boss(boss.id());
            if !game.player.attack_tracker.has_hit(target) {
                game.player.attack_tracker.mark_hit(target);
                let dmg = DamageInfo {
                    damage: attack_damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: if is_heavy { 40.0 } else { 20.0 },
                    attacker_id: game.player.id(),
                    parryable: false,
                };
                let outcome = boss.take_damage(&dmg);
                if !outcome.was_ignored {
                    game.damage_dealt += outcome.actual_damage as u32;
                    game.damage_numbers.push(DamageNumber {
                        x: bx,
                        y: by - 36.0,
                        vy: -42.0,
                        value: outcome.actual_damage,
                        timer: 0.8,
                        is_player_damage: false,
                    });
                    game.camera.add_shake(if is_heavy { 8.0 } else { 4.0 });
                    game.audio.play_sfx("hit", 0.12, 0.0);
                }
                if outcome.killed && !game.boss_defeated {
                    game.boss_defeated = true;
                    let boss_name = match boss.boss_type {
                        BossType::IudexGundyr => "IudexGundyr",
                        BossType::Vordt => "Vordt",
                        BossType::DemonKnight => "CurseRottedGreatwood",
                        BossType::Dragonrider => "DeaconsOfTheDeep",
                        BossType::RuinSentinel => "PontiffSulyvahn",
                    };
                    if !game.bosses_defeated.iter().any(|b| b == boss_name) {
                        game.bosses_defeated.push(boss_name.into());
                    }
                    gundyr_door = boss.boss_type == BossType::IudexGundyr && !game.gundyr_door_open;
                    for gate in &mut game.fog_gates {
                        if gate.destination == game.area {
                            gate.active = false;
                        }
                    }
                    if game.bosses_defeated.len() >= 5 {
                        game.state = crate::game::GameState::Victory;
                    }
                    game.souls += 5000;
                    game.camera.add_shake(15.0);
                    game.slow_motion_timer = 1.5;
                    game.audio.play_sfx("boss_die", 0.2, 0.0);
                }
            }
        }

        if boss.current_attack_can_hit(px, py) && game.boss_intro_timer <= 0.0 {
            if *game.player.state() != EntityState::Rolling {
                let dmg = DamageInfo {
                    damage: boss.damage,
                    knockback_x: 0.0,
                    knockback_y: 0.0,
                    poise_damage: 15.0,
                    attacker_id: boss.id(),
                    parryable: boss.current_attack_can_be_parried(),
                };
                let outcome = game.player.take_damage(&dmg);

                if outcome.was_parried && boss.current_attack_can_be_parried() {
                    boss.state = EntityState::Staggered;
                    boss.stagger_timer = 2.0;
                    game.riposte_timer = 2.0;
                    game.riposte_target_id = boss.id();
                    game.screen_flash = Some(ScreenFlash { timer: 0.12, max_timer: 0.12, color: [0.2, 1.0, 1.0, 0.4] });
                    game.stagger_bursts.push(BlockSpark { x: (px + bx) * 0.5, y: (py + by) * 0.5, timer: 0.3 });
                    game.audio.play_sfx("hit", 0.18, 0.0);
                } else if outcome.was_blocked {
                    game.damage_taken += outcome.actual_damage as u32;
                    game.audio.play_sfx("hit", 0.1, 0.0);
                } else if outcome.actual_damage > 0 {
                    game.camera.add_shake(12.0);
                    game.audio.play_sfx("player_hit", 0.18, 0.0);
                    game.damage_taken += outcome.actual_damage as u32;
                    game.damage_numbers.push(DamageNumber {
                        x: px,
                        y: py - 24.0,
                        vy: -50.0,
                        value: outcome.actual_damage,
                        timer: 0.8,
                        is_player_damage: true,
                    });
                }
                boss.mark_current_hit_window();
            }
        }
    }

    // Open Gundyr's door after defeat
    if gundyr_door {
        game.gundyr_door_open = true;
        fill_tiles(&mut game.chunk, TileId::Ground, 16, 8, 40, 18);
        for gate in &mut game.fog_gates {
            if gate.destination == AreaId::FirelinkShrine {
                gate.active = true;
            }
        }
        rebuild_collision(game);
    }

    // Spawn boss when last enemy killed in areas without dedicated boss
    let has_area_boss = area_boss(game.area).is_some();
    if !has_area_boss && !game.boss_active && !game.boss_defeated && game.enemies.last().map_or(false, |e| e.is_dead()) {
        let boss_type = (game.enemies_killed * 1103515245 + 12345) as usize % 3;
        let (px, py) = game.player.position();
        let spawn_x = px + 200.0;
        let spawn_y = py;
        game.boss = Some(match boss_type {
            0 => crate::entity::boss::Boss::new_test_boss(10, spawn_x, spawn_y),
            1 => crate::entity::boss::Boss::new_dragonrider(10, spawn_x, spawn_y),
            _ => crate::entity::boss::Boss::new_ruin_sentinel(10, spawn_x, spawn_y),
        });
        game.boss_active = true;
        game.boss_intro_timer = 3.0;
    }
}
