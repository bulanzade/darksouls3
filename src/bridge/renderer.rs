use crate::bridge::wasm_entry::{
    area_has_bonfire, Game, ItemKind, NpcKind,
};
use crate::entity::entity_trait::{Entity, EntityState};
use crate::game::GameState;
use crate::render::ui_renderer::UiRenderer;
use crate::render::vertex::InstanceData;
use crate::world::chunk::CHUNK_SIZE;
use crate::world::tileset::{TileId, TILE_SIZE};
use web_sys::WebGl2RenderingContext as GL;

pub(crate) fn render(game: &mut Game) {
    let gl = &game.gl_ctx.gl;
    let player_hp_ratio = game.player.hp as f32 / game.player.max_hp as f32;

    // --- Pass 1: Render scene to FBO ---
    gl.bind_framebuffer(GL::FRAMEBUFFER, Some(&game.scene_fbo));
    gl.viewport(0, 0, game.screen_w as i32, game.screen_h as i32);
    game.gl_ctx.clear(0.02, 0.02, 0.04, 1.0);

    let projection = game.camera.projection_matrix();
    game.batcher.set_projection(gl, &projection);

    // --- Draw tilemap (only visible tiles) ---
    let (off_x, off_y) = game.chunk.world_offset();
    let tile_size = TILE_SIZE as f32;
    let cam_x = game.camera.x;
    let cam_y = game.camera.y;
    let half_w = game.screen_w * 0.5 + tile_size;
    let half_h = game.screen_h * 0.5 + tile_size;

    let min_tx = (((cam_x - half_w - off_x) / tile_size).floor() as i32).max(0);
    let max_tx = (((cam_x + half_w - off_x) / tile_size).ceil() as i32).min(CHUNK_SIZE as i32 - 1);
    let min_ty = (((cam_y - half_h - off_y) / tile_size).floor() as i32).max(0);
    let max_ty = (((cam_y + half_h - off_y) / tile_size).ceil() as i32).min(CHUNK_SIZE as i32 - 1);

    for y in min_ty as usize..=max_ty as usize {
        for x in min_tx as usize..=max_tx as usize {
            let tile_id = game.chunk.tiles[y][x];
            if tile_id == TileId::Empty {
                continue;
            }
            let def = match game.tileset.get(tile_id) {
                Some(d) => d,
                None => continue,
            };
            let px = off_x + x as f32 * tile_size + tile_size * 0.5;
            let py = off_y + y as f32 * tile_size + tile_size * 0.5;
            let instance = InstanceData::new(
                px,
                py,
                tile_size,
                tile_size,
                [def.uv_x, def.uv_y, def.uv_x + def.uv_w, def.uv_y + def.uv_h],
                [1.0, 1.0, 1.0, 1.0],
            );
            game.batcher.draw(instance, &game.tileset_texture, gl);
        }
    }

    // --- Draw bonfire ---
    if area_has_bonfire(game.area) {
        let pulse = (game.time.accumulator as f32 * 1.5).sin() * 0.15 + 0.85;
        game.batcher.draw(
            InstanceData::new(game.bonfire_x, game.bonfire_y, 64.0 * pulse, 64.0 * pulse, [0.0, 0.0, 1.0, 1.0], [0.9, 0.6, 0.1, 0.12]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(game.bonfire_x, game.bonfire_y, 48.0 * pulse, 48.0 * pulse, [0.0, 0.0, 1.0, 1.0], [1.0, 0.7, 0.2, 0.15]),
            &game.white_tex, gl,
        );
        let bonfire_data = InstanceData::new(
            game.bonfire_x, game.bonfire_y,
            32.0, 32.0,
            [0.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
        );
        game.batcher.draw(bonfire_data, &game.bonfire_tex, gl);
    }

    // --- Draw fog gates as doorways ---
    {
        let pulse = (game.time.accumulator as f32 * 1.2).sin() * 0.1 + 0.9;
        for gate in &game.fog_gates {
            if !gate.active { continue; }
            let is_boss = gate.destination == game.area;
            let is_vertical = gate.h > gate.w;
            let (frame_color, fog_color) = if is_boss {
                ([0.5f32, 0.3, 0.1, 1.0], [0.5, 0.2, 0.7, 0.5 * pulse])
            } else {
                ([0.4f32, 0.35, 0.25, 1.0], [0.3, 0.5, 0.7, 0.35 * pulse])
            };
            if is_vertical {
                let pillar_w = 8.0;
                let pillar_h = gate.h;
                game.batcher.draw(
                    InstanceData::new(gate.x - gate.w * 0.5 - pillar_w * 0.5, gate.y, pillar_w, pillar_h, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                game.batcher.draw(
                    InstanceData::new(gate.x + gate.w * 0.5 + pillar_w * 0.5, gate.y, pillar_w, pillar_h, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y, gate.w, gate.h, [0.0, 0.0, 1.0, 1.0], fog_color),
                    &game.white_tex, gl,
                );
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y - gate.h * 0.5 - 3.0, gate.w + pillar_w * 2.0, 6.0, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
            } else {
                let pillar_w = gate.w;
                let pillar_h = 8.0;
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y - gate.h * 0.5 - pillar_h * 0.5, pillar_w, pillar_h, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y + gate.h * 0.5 + pillar_h * 0.5, pillar_w, pillar_h, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                game.batcher.draw(
                    InstanceData::new(gate.x, gate.y, gate.w, gate.h, [0.0, 0.0, 1.0, 1.0], fog_color),
                    &game.white_tex, gl,
                );
                game.batcher.draw(
                    InstanceData::new(gate.x - gate.w * 0.5 - 3.0, gate.y, 6.0, gate.h + pillar_h * 2.0, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
                game.batcher.draw(
                    InstanceData::new(gate.x + gate.w * 0.5 + 3.0, gate.y, 6.0, gate.h + pillar_h * 2.0, [0.0, 0.0, 1.0, 1.0], frame_color),
                    &game.white_tex, gl,
                );
            }
        }
    }

    // --- Draw wall torches (at light positions, skip player light [0] and bonfire light [1]) ---
    for i in 2..game.lights.len() {
        let light = &game.lights[i];
        let flicker = (game.time.accumulator as f32 * (3.0 + i as f32 * 0.7)).sin() * 0.2 + 0.8;
        game.batcher.draw(
            InstanceData::new(light.x, light.y - 6.0, 6.0, 8.0, [0.0, 0.0, 1.0, 1.0], [0.5, 0.35, 0.2, 1.0]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(light.x, light.y - 12.0, 5.0 * flicker, 6.0 * flicker, [0.0, 0.0, 1.0, 1.0], [1.0, 0.6, 0.1, 0.9]),
            &game.white_tex, gl,
        );
    }

    // --- Draw world items ---
    for item in &game.items {
        if item.collected { continue; }
        let (r, g, b) = match &item.kind {
            ItemKind::SoulOrb(_) => (0.6, 0.8, 1.0),
            ItemKind::EstusShard => (0.2, 0.9, 0.3),
            ItemKind::HomewardBone => (0.8, 0.7, 0.5),
            ItemKind::PurpleMoss => (0.6, 0.2, 0.8),
            ItemKind::WeaponDrop(_) => (0.9, 0.6, 0.1),
            ItemKind::ArmorDrop(_, _) => (0.5, 0.5, 0.8),
            ItemKind::RingDrop(_) => (0.9, 0.8, 0.2),
            ItemKind::TitaniteShard => (0.3, 0.7, 0.3),
            ItemKind::Firebomb => (0.9, 0.3, 0.1),
            ItemKind::Ember => (0.9, 0.6, 0.1),
            ItemKind::UndeadBoneShard => (0.8, 0.8, 0.7),
            ItemKind::Consumable(_) => (0.6, 0.4, 0.8),
        };
        let bob = (item.y * 0.05).sin() * 3.0;
        game.batcher.draw(
            InstanceData::new(item.x, item.y + bob, 12.0, 12.0, [0.0, 0.0, 1.0, 1.0], [r, g, b, 0.9]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(item.x, item.y + bob, 20.0, 20.0, [0.0, 0.0, 1.0, 1.0], [r, g, b, 0.2]),
            &game.white_tex, gl,
        );
    }

    // --- Draw treasure chests ---
    for chest in &game.chests {
        if chest.mimic_revealed { continue; }
        let (color, size) = if chest.opened {
            ([0.4, 0.35, 0.25, 0.6], 16.0)
        } else {
            ([0.8, 0.65, 0.2, 1.0], 20.0)
        };
        game.batcher.draw(
            InstanceData::new(chest.x, chest.y, size, size * 0.7, [0.0, 0.0, 1.0, 1.0], color),
            &game.white_tex, gl,
        );
        if !chest.opened {
            game.batcher.draw(
                InstanceData::new(chest.x, chest.y - 2.0, 6.0, 4.0, [0.0, 0.0, 1.0, 1.0], [0.9, 0.8, 0.3, 1.0]),
                &game.white_tex, gl,
            );
            game.batcher.draw(
                InstanceData::new(chest.x, chest.y, size + 10.0, size + 10.0, [0.0, 0.0, 1.0, 1.0], [0.8, 0.6, 0.1, 0.15]),
                &game.white_tex, gl,
            );
        }
    }

    // --- Draw bloodstain ---
    if game.has_bloodstain {
        let pulse = (game.time.accumulator as f32).sin() * 0.3 + 0.7;
        game.batcher.draw(
            InstanceData::new(game.bloodstain_x, game.bloodstain_y, 32.0 * pulse, 32.0 * pulse, [0.0, 0.0, 1.0, 1.0], [0.8, 0.1, 0.1, 0.2 * pulse]),
            &game.white_tex, gl,
        );
        let bloodstain_data = InstanceData::new(
            game.bloodstain_x, game.bloodstain_y,
            16.0, 16.0,
            [0.0, 0.0, 1.0, 1.0],
            [0.9, 0.15, 0.15, 0.8],
        );
        game.batcher.draw(bloodstain_data, &game.white_tex, gl);
    }

    // --- Draw NPCs ---
    for npc in &game.npcs {
        let bob = (game.play_time * 2.0).sin() * 2.0;
        let (body_w, body_h, head_size) = match npc.kind {
            NpcKind::Blacksmith => (24.0, 28.0, 12.0),
            NpcKind::Merchant => (20.0, 24.0, 10.0),
            NpcKind::LevelUp => (22.0, 30.0, 11.0),
            _ => (22.0, 26.0, 10.0),
        };
        game.batcher.draw(
            InstanceData::new(npc.x, npc.y + bob, body_w, body_h, [0.0, 0.0, 1.0, 1.0], npc.color),
            &game.white_tex, gl,
        );
        let head_color = [
            (npc.color[0] + 0.3).min(1.0),
            (npc.color[1] + 0.3).min(1.0),
            (npc.color[2] + 0.3).min(1.0),
            1.0,
        ];
        game.batcher.draw(
            InstanceData::new(npc.x, npc.y - body_h * 0.5 - head_size * 0.5 + bob, head_size, head_size, [0.0, 0.0, 1.0, 1.0], head_color),
            &game.white_tex, gl,
        );
        let proximity = {
            let dx = game.player.transform.x - npc.x;
            let dy = game.player.transform.y - npc.y;
            (dx * dx + dy * dy).sqrt() < 50.0
        };
        if proximity {
            let flash = (game.play_time * 4.0).sin() * 0.3 + 0.7;
            game.batcher.draw(
                InstanceData::new(npc.x, npc.y - body_h * 0.5 - head_size - 6.0, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.0, flash]),
                &game.white_tex, gl,
            );
        }
    }

    // --- Draw enemies ---
    for enemy in &game.enemies {
        if !enemy.is_dead() {
            enemy.render(&mut game.batcher, &game.enemy_tex, gl);
            let (ex, ey) = enemy.position();
            let hp_ratio = enemy.hp as f32 / enemy.max_hp as f32;
            let bar_w = 26.0;
            let bar_h = 3.0;
            let bar_y = ey - 20.0;
            game.batcher.draw(
                InstanceData::new(ex, bar_y, bar_w, bar_h, [0.0, 0.0, 1.0, 1.0], [0.2, 0.2, 0.2, 0.8]),
                &game.white_tex, gl,
            );
            let fg_w = bar_w * hp_ratio;
            let fg_x = ex - bar_w * 0.5 + fg_w * 0.5;
            let hp_color: [f32; 4] = if hp_ratio > 0.5 {
                [0.2, 0.8, 0.2, 0.9]
            } else if hp_ratio > 0.25 {
                [0.8, 0.8, 0.2, 0.9]
            } else {
                [0.9, 0.2, 0.2, 0.9]
            };
            game.batcher.draw(
                InstanceData::new(fg_x, bar_y, fg_w, bar_h, [0.0, 0.0, 1.0, 1.0], hp_color),
                &game.white_tex, gl,
            );
        }
    }

    // --- Draw projectiles (arrows) ---
    for proj in &game.projectiles {
        game.batcher.draw(
            InstanceData::new(proj.x, proj.y, 8.0, 3.0, [0.0, 0.0, 1.0, 1.0], [0.8, 0.6, 0.2, 1.0]),
            &game.white_tex, gl,
        );
    }

    // --- Draw block sparks ---
    for spark in &game.block_sparks {
        let alpha = spark.timer / 0.3;
        for i in 0..4 {
            let angle = (i as f32 / 4.0) * std::f32::consts::TAU + spark.timer * 10.0;
            let r = 12.0 * (1.0 - alpha);
            let ox = spark.x + angle.cos() * r;
            let oy = spark.y + angle.sin() * r;
            game.batcher.draw(
                InstanceData::new(ox, oy, 8.0, 8.0, [0.0, 0.0, 1.0, 1.0], [0.5, 0.7, 1.0, alpha]),
                &game.white_tex, gl,
            );
        }
        game.batcher.draw(
            InstanceData::new(spark.x, spark.y, 20.0, 20.0, [0.0, 0.0, 1.0, 1.0], [0.3, 0.5, 1.0, alpha * 0.4]),
            &game.white_tex, gl,
        );
    }

    // --- Draw stagger bursts ---
    for burst in &game.stagger_bursts {
        let alpha = burst.timer / 0.2;
        let size = 24.0 * (1.0 - alpha) + 8.0;
        game.batcher.draw(
            InstanceData::new(burst.x, burst.y, size, size, [0.0, 0.0, 1.0, 1.0], [1.0, 0.9, 0.3, alpha * 0.5]),
            &game.white_tex, gl,
        );
    }

    // --- Draw dust particles ---
    for dust in &game.dust_particles {
        let alpha = dust.timer / 0.4;
        game.batcher.draw(
            InstanceData::new(dust.x, dust.y, 6.0, 6.0, [0.0, 0.0, 1.0, 1.0], [0.7, 0.65, 0.5, alpha * 0.6]),
            &game.white_tex, gl,
        );
    }

    // --- Draw damage numbers ---
    for dn in &game.damage_numbers {
        let alpha = (dn.timer / 0.8).min(1.0);
        let color: [f32; 4] = if dn.is_player_damage {
            [1.0, 0.3, 0.3, alpha]
        } else {
            [1.0, 1.0, 0.5, alpha]
        };
        let size = 6.0 + (dn.value as f32 / 20.0).min(8.0);
        game.batcher.draw(
            InstanceData::new(dn.x, dn.y, size + 2.0, size + 2.0, [0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 0.0, alpha * 0.5]),
            &game.white_tex, gl,
        );
        game.batcher.draw(
            InstanceData::new(dn.x, dn.y, size, size, [0.0, 0.0, 1.0, 1.0], color),
            &game.white_tex, gl,
        );
    }

    // --- Draw death dissolve particles ---
    for p in &game.death_particles {
        let alpha = (p.timer / 0.7).min(1.0);
        game.batcher.draw(
            InstanceData::new(p.x, p.y, p.size, p.size, [0.0, 0.0, 1.0, 1.0], [0.4, 0.3, 0.2, alpha * 0.8]),
            &game.white_tex, gl,
        );
    }

    if let Some(ref boss) = game.boss {
        if !boss.is_dead() && boss.boss_activated {
            boss.render(&mut game.batcher, &game.boss_tex, gl);
            let (bx, by) = boss.position();
            let hp_ratio = boss.hp as f32 / boss.max_hp as f32;
            let bar_w = 48.0;
            let bar_h = 4.0;
            let bar_y = by - 34.0;
            game.batcher.draw(
                InstanceData::new(bx, bar_y, bar_w, bar_h, [0.0, 0.0, 1.0, 1.0], [0.2, 0.2, 0.2, 0.8]),
                &game.white_tex, gl,
            );
            let fg_w = bar_w * hp_ratio;
            let fg_x = bx - bar_w * 0.5 + fg_w * 0.5;
            game.batcher.draw(
                InstanceData::new(fg_x, bar_y, fg_w, bar_h, [0.0, 0.0, 1.0, 1.0], [0.8, 0.2, 0.8, 0.9]),
                &game.white_tex, gl,
            );
        }
    }

    // --- Draw soul orbs ---
    for orb in &game.soul_orbs {
        let alpha = (orb.timer / orb.max_time).min(1.0);
        game.batcher.draw(
            InstanceData::new(orb.x, orb.y, 8.0, 8.0, [0.0, 0.0, 1.0, 1.0], [0.6, 0.8, 1.0, alpha]),
            &game.white_tex, gl,
        );
    }

    // --- Draw player ---
    game.player.render(&mut game.batcher, &game.player_tex, gl);

    // --- Lock-on indicator (diamond above locked target) ---
    if let Some((tx, ty)) = game.lock_on_pos {
        let pulse = 0.8 + (game.state_timer * 6.0).sin() * 0.2;
        let size = 12.0 * pulse;
        let ly = ty - 30.0;
        let angle = game.state_timer * 2.0;
        let dx1 = angle.cos() * size * 0.5;
        let dy1 = angle.sin() * size * 0.5;
        game.batcher.draw(InstanceData::new(tx + dx1, ly + dy1, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 0.8, 0.2, 0.9]), &game.white_tex, gl);
        game.batcher.draw(InstanceData::new(tx - dy1, ly + dx1, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 0.8, 0.2, 0.9]), &game.white_tex, gl);
        game.batcher.draw(InstanceData::new(tx - dx1, ly - dy1, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 0.8, 0.2, 0.9]), &game.white_tex, gl);
        game.batcher.draw(InstanceData::new(tx + dy1, ly - dx1, 4.0, 4.0, [0.0, 0.0, 1.0, 1.0], [1.0, 0.8, 0.2, 0.9]), &game.white_tex, gl);
    }

    // --- Heal effect ---
    if game.heal_effect_timer > 0.0 {
        let (px, py) = game.player.position();
        let t = game.heal_effect_timer;
        let alpha = t / 0.8;
        for i in 0..6 {
            let angle = (i as f32 / 6.0) * std::f32::consts::TAU + t * 4.0;
            let radius = 20.0 * (1.0 - alpha);
            let ox = px + angle.cos() * radius;
            let oy = py + angle.sin() * radius;
            game.batcher.draw(
                InstanceData::new(ox, oy, 6.0, 6.0, [0.0, 0.0, 1.0, 1.0], [0.2, 0.9, 0.3, alpha * 0.8]),
                &game.white_tex, gl,
            );
        }
        game.batcher.draw(
            InstanceData::new(px, py, 40.0 * (1.0 + (1.0 - alpha) * 0.5), 40.0 * (1.0 + (1.0 - alpha) * 0.5), [0.0, 0.0, 1.0, 1.0], [0.3, 1.0, 0.4, alpha * 0.3]),
            &game.white_tex, gl,
        );
    }

    // --- Draw attack swing effect ---
    if *game.player.state() == EntityState::Attacking {
        let (px, py) = game.player.position();
        let facing = game.player.facing;
        let t = game.player.attack_timer;
        let total = if game.player.is_heavy_attack { game.player.heavy_attack_duration() } else { game.player.light_attack_duration() };
        let progress = 1.0 - (t / total);
        let range = if game.player.is_heavy_attack { 36.0 } else { 28.0 };
        let arc_span = if game.player.is_heavy_attack { 1.2 } else { 0.8 };
        let steps = if game.player.is_heavy_attack { 8 } else { 5 };
        for i in 0..steps {
            let frac = i as f32 / steps as f32;
            let arc_t = (frac + progress * 0.3).min(1.0);
            let angle = facing - arc_span * 0.5 + arc_span * arc_t;
            let dist = range * (0.6 + frac * 0.4);
            let sx = px + angle.cos() * dist;
            let sy = py + angle.sin() * dist;
            let alpha = (1.0 - frac) * 0.6 * (1.0 - progress * 0.5);
            let size = if game.player.is_heavy_attack { 10.0 - frac * 4.0 } else { 7.0 - frac * 3.0 };
            let color: [f32; 4] = if game.player.is_heavy_attack {
                [1.0, 0.6 + frac * 0.2, 0.1, alpha]
            } else {
                [1.0, 0.9, 0.5, alpha]
            };
            game.batcher.draw(
                InstanceData::new(sx, sy, size, size * 0.4, [0.0, 0.0, 1.0, 1.0], color),
                &game.white_tex, gl,
            );
        }
        if progress > 0.3 && progress < 0.7 {
            let sx = px + facing.cos() * range;
            let sy = py + facing.sin() * range;
            let alpha = 0.4 * (1.0 - (progress - 0.3) / 0.4);
            game.batcher.draw(
                InstanceData::new(sx, sy, 16.0, 16.0, [0.0, 0.0, 1.0, 1.0], [1.0, 1.0, 1.0, alpha]),
                &game.white_tex, gl,
            );
        }
    }

    game.batcher.flush(gl);

    // --- Pass 2: Post-processing composite to screen ---
    gl.bind_framebuffer(GL::FRAMEBUFFER, None);
    gl.viewport(0, 0, game.screen_w as i32, game.screen_h as i32);
    gl.clear_color(0.0, 0.0, 0.0, 1.0);
    gl.clear(GL::COLOR_BUFFER_BIT);

    gl.active_texture(GL::TEXTURE0);
    gl.bind_texture(GL::TEXTURE_2D, Some(&game.scene_texture));
    let (brightness, saturation, fog_color) = if player_hp_ratio < 0.25 {
        (0.9, 0.6, [0.08, 0.02, 0.02, 0.7])
    } else {
        (1.0, 0.85, [0.02, 0.02, 0.04, 0.6])
    };
    game.post_processor.render(
        gl,
        1.2,
        fog_color,
        [game.screen_h * 0.3, game.screen_h * 0.7],
        brightness,
        saturation,
    );

    // --- HUD projection ---
    let ui_proj = UiRenderer::screen_projection(game.screen_w, game.screen_h);

    // --- Screen flash ---
    if let Some(ref flash) = game.screen_flash {
        let alpha = flash.timer / flash.max_timer;
        let c = flash.color;
        game.ui_renderer.draw_bar(
            gl, game.screen_w * 0.5, game.screen_h * 0.5,
            game.screen_w, game.screen_h,
            1.0,
            [c[0], c[1], c[2], c[3] * alpha],
            [c[0], c[1], c[2], c[3] * alpha],
            &ui_proj,
        );
    }

    // --- Poison overlay ---
    if game.player.poison_timer > 0.0 {
        let pulse = (game.time.accumulator as f32 * 2.0).sin() * 0.1 + 0.15;
        game.ui_renderer.draw_bar(
            gl, game.screen_w * 0.5, game.screen_h * 0.5,
            game.screen_w, game.screen_h,
            1.0,
            [0.0, 0.3, 0.0, pulse],
            [0.0, 0.3, 0.0, pulse],
            &ui_proj,
        );
    }

    // --- HUD bars ---
    let hp_ratio = player_hp_ratio;
    let hp_bar_w = 200.0;
    let hp_bar_h = 16.0;
    let hp_bar_x = 20.0 + hp_bar_w * 0.5;
    game.ui_renderer.draw_bar(
        gl, hp_bar_x, 20.0, hp_bar_w, hp_bar_h,
        hp_ratio,
        [0.15, 0.15, 0.15, 0.8],
        [0.7, 0.1, 0.1, 0.9],
        &ui_proj,
    );

    let stamina_ratio = game.player.stamina.current / game.player.stamina.maximum;
    let sta_bar_w = 200.0;
    let sta_bar_h = 12.0;
    let sta_bar_x = 20.0 + sta_bar_w * 0.5;
    game.ui_renderer.draw_bar(
        gl, sta_bar_x, 42.0, sta_bar_w, sta_bar_h,
        stamina_ratio,
        [0.15, 0.15, 0.15, 0.8],
        [0.1, 0.5, 0.1, 0.9],
        &ui_proj,
    );

    // Boss HP bar (center top)
    if let Some(ref boss) = game.boss {
        if !boss.is_dead() && boss.boss_activated {
            let boss_hp_ratio = boss.hp as f32 / boss.max_hp as f32;
            let boss_bar_w = 400.0;
            let boss_bar_x = game.screen_w * 0.5;
            game.ui_renderer.draw_bar(
                gl, boss_bar_x, 20.0, boss_bar_w, 14.0,
                boss_hp_ratio,
                [0.15, 0.15, 0.15, 0.8],
                [0.8, 0.2, 0.8, 0.9],
                &ui_proj,
            );
        }
    }

    // Estus indicator
    {
        let flask_size = 10.0;
        let flask_gap = 3.0;
        let start_x = 20.0;
        let flask_y = 58.0;
        for i in 0..game.bonfire.estus_max {
            let x = start_x + flask_size * 0.5 + i as f32 * (flask_size + flask_gap);
            let filled = i < game.bonfire.estus_charges;
            let color: [f32; 4] = if filled {
                [0.9, 0.7, 0.1, 0.9]
            } else {
                [0.2, 0.2, 0.2, 0.6]
            };
            game.ui_renderer.draw_bar(
                gl, x, flask_y, flask_size, flask_size,
                1.0, color, color, &ui_proj,
            );
        }
    }

    // --- Equipment Slot UI ---
    {
        let slot_size = 40.0;
        let gap = 4.0;
        let base_x = 30.0 + slot_size + gap;
        let base_y = game.screen_h - 30.0 - slot_size - gap;
        let bg_color = [0.08f32, 0.08, 0.08, 0.85];
        let border_color = [0.35f32, 0.3, 0.25, 0.9];

        let spell_x = base_x;
        let spell_y = base_y - slot_size - gap;
        let item_x = base_x;
        let item_y = base_y + slot_size + gap;
        let left_x = base_x - slot_size - gap;
        let left_y = base_y;
        let right_x = base_x + slot_size + gap;
        let right_y = base_y;

        let draw_slot = |gl: &GL, x: f32, y: f32| {
            game.ui_renderer.draw_bar(gl, x, y, slot_size, slot_size, 1.0, bg_color, bg_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, x, y - slot_size * 0.5, slot_size, 1.5, 1.0, border_color, border_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, x, y + slot_size * 0.5, slot_size, 1.5, 1.0, border_color, border_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, x - slot_size * 0.5, y, 1.5, slot_size, 1.0, border_color, border_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, x + slot_size * 0.5, y, 1.5, slot_size, 1.0, border_color, border_color, &ui_proj);
        };

        draw_slot(gl, spell_x, spell_y);
        draw_slot(gl, item_x, item_y);
        draw_slot(gl, left_x, left_y);
        draw_slot(gl, right_x, right_y);

        let icon_dim = [0.0f32, 0.0, 1.0, 1.0];
        let spell_dim = [0.25f32, 0.2, 0.35, 0.5];
        game.ui_renderer.draw_bar(gl, spell_x, spell_y, 14.0, 14.0, 1.0, icon_dim, spell_dim, &ui_proj);
        game.ui_renderer.draw_bar(gl, spell_x, spell_y - 3.0, 8.0, 8.0, 1.0, spell_dim, spell_dim, &ui_proj);
        game.ui_renderer.draw_bar(gl, spell_x, spell_y + 3.0, 8.0, 8.0, 1.0, spell_dim, spell_dim, &ui_proj);

        let flask_color = [0.9f32, 0.7, 0.1, 0.8];
        game.ui_renderer.draw_bar(gl, item_x, item_y + 2.0, 12.0, 16.0, 1.0, icon_dim, flask_color, &ui_proj);
        game.ui_renderer.draw_bar(gl, item_x, item_y - 8.0, 6.0, 6.0, 1.0, icon_dim, flask_color, &ui_proj);
        let cap_color = [0.7f32, 0.5, 0.2, 0.8];
        game.ui_renderer.draw_bar(gl, item_x, item_y - 12.0, 8.0, 3.0, 1.0, icon_dim, cap_color, &ui_proj);

        let is_shield = game.player.equipment.left_hand.active().weapon_type == crate::combat::weapon::WeaponType::Shield;
        let left_is_fist = game.player.equipment.left_hand.active().weapon_type == crate::combat::weapon::WeaponType::Fist;
        if is_shield {
            let shield_color = [0.3f32, 0.5, 0.8, 0.8];
            game.ui_renderer.draw_bar(gl, left_x, left_y, 18.0, 22.0, 1.0, icon_dim, shield_color, &ui_proj);
            let cross_color = [0.9f32, 0.8, 0.3, 0.9];
            game.ui_renderer.draw_bar(gl, left_x, left_y, 2.0, 14.0, 1.0, icon_dim, cross_color, &ui_proj);
            game.ui_renderer.draw_bar(gl, left_x, left_y - 2.0, 12.0, 2.0, 1.0, icon_dim, cross_color, &ui_proj);
        } else if !left_is_fist {
            let wep_color = [0.6f32, 0.6, 0.65, 0.8];
            game.ui_renderer.draw_bar(gl, left_x, left_y - 4.0, 3.0, 20.0, 1.0, icon_dim, wep_color, &ui_proj);
            let guard_color = [0.5f32, 0.35, 0.2, 0.9];
            game.ui_renderer.draw_bar(gl, left_x, left_y + 6.0, 12.0, 3.0, 1.0, icon_dim, guard_color, &ui_proj);
        }

        let right_is_fist = game.player.weapon.weapon_type == crate::combat::weapon::WeaponType::Fist;
        if !right_is_fist {
            let sword_color = [0.75f32, 0.75, 0.8, 0.85];
            game.ui_renderer.draw_bar(gl, right_x, right_y - 4.0, 3.0, 20.0, 1.0, icon_dim, sword_color, &ui_proj);
            let guard_color2 = [0.5f32, 0.35, 0.2, 0.9];
            game.ui_renderer.draw_bar(gl, right_x, right_y + 6.0, 14.0, 3.0, 1.0, icon_dim, guard_color2, &ui_proj);
            let pommel_color = [0.4f32, 0.3, 0.2, 0.8];
            game.ui_renderer.draw_bar(gl, right_x, right_y + 14.0, 5.0, 5.0, 1.0, icon_dim, pommel_color, &ui_proj);
        }
    }

    // --- Mini-map ---
    {
        let map_size = 150.0;
        let map_left = game.screen_w - map_size - 10.0;
        let map_top = 10.0;
        let map_cx = map_left + map_size * 0.5;
        let map_cy = map_top + map_size * 0.5;
        let world_size = CHUNK_SIZE as f32 * TILE_SIZE as f32;
        let scale = map_size / world_size;

        game.ui_renderer.draw_bar(
            gl, map_cx, map_cy, map_size + 4.0, map_size + 4.0,
            1.0, [0.0, 0.0, 0.0, 0.7], [0.0, 0.0, 0.0, 0.7], &ui_proj,
        );

        let step = 4;
        for ty in (0..CHUNK_SIZE).step_by(step) {
            for tx in (0..CHUNK_SIZE).step_by(step) {
                let tile = game.chunk.tiles[ty][tx];
                if tile == TileId::Empty { continue; }
                let is_wall = tile == TileId::Wall;
                let color: [f32; 4] = if is_wall {
                    [0.25, 0.22, 0.2, 0.9]
                } else {
                    [0.55, 0.48, 0.35, 1.0]
                };
                let dot_x = map_left + (tx as f32 * TILE_SIZE as f32) * scale;
                let dot_y = map_top + (ty as f32 * TILE_SIZE as f32) * scale;
                let s = step as f32 * TILE_SIZE as f32 * scale;
                game.ui_renderer.draw_bar(
                    gl, dot_x + s * 0.5, dot_y + s * 0.5, s, s,
                    1.0, color, color, &ui_proj,
                );
            }
        }

        let (ppx, ppy) = game.player.position();
        let pdx = map_left + ppx * scale;
        let pdy = map_top + ppy * scale;
        game.ui_renderer.draw_bar(
            gl, pdx, pdy, 6.0, 6.0,
            1.0, [0.2, 0.9, 1.0, 1.0], [0.2, 0.9, 1.0, 1.0], &ui_proj,
        );

        for enemy in &game.enemies {
            if enemy.is_dead() { continue; }
            let (ex, ey) = enemy.position();
            let edx = map_left + ex * scale;
            let edy = map_top + ey * scale;
            game.ui_renderer.draw_bar(
                gl, edx, edy, 4.0, 4.0,
                1.0, [1.0, 0.2, 0.2, 1.0], [1.0, 0.2, 0.2, 1.0], &ui_proj,
            );
        }

        if let Some(ref boss) = game.boss {
            if !boss.is_dead() {
                let (bx, by) = boss.position();
                let bdx = map_left + bx * scale;
                let bdy = map_top + by * scale;
                game.ui_renderer.draw_bar(
                    gl, bdx, bdy, 6.0, 6.0,
                    1.0, [0.9, 0.1, 0.9, 1.0], [0.9, 0.1, 0.9, 1.0], &ui_proj,
                );
            }
        }

        if area_has_bonfire(game.area) {
            let bfx = map_left + game.bonfire_x * scale;
            let bfy = map_top + game.bonfire_y * scale;
            game.ui_renderer.draw_bar(
                gl, bfx, bfy, 4.0, 4.0,
                1.0, [1.0, 0.7, 0.2, 1.0], [1.0, 0.7, 0.2, 1.0], &ui_proj,
            );
        }
    }

    // --- State overlays ---
    match game.state {
        GameState::TitleScreen | GameState::DeathScreen | GameState::Victory | GameState::LevelUpMenu => {
            let alpha = match game.state {
                GameState::DeathScreen => (game.death_anim_timer / 1.5).min(0.85),
                _ => {
                    let a = if matches!(game.state, GameState::TitleScreen) { 0.5 }
                            else if matches!(game.state, GameState::LevelUpMenu) { 0.6 }
                            else { 0.6 };
                    a
                }
            };
            game.ui_renderer.draw_bar(
                gl, game.screen_w * 0.5, game.screen_h * 0.5,
                game.screen_w, game.screen_h,
                1.0,
                [0.0, 0.0, 0.0, alpha],
                [0.0, 0.0, 0.0, alpha],
                &ui_proj,
            );
        }
        _ => {}
    }

    // --- DOM text overlay ---
    super::dom_ui::update(game);
}
