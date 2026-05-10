use crate::bridge::wasm_entry::{
    area_has_bonfire, area_name, Game, InventoryItemKind, MenuTab,
};
use crate::entity::entity_trait::{Entity, EntityState};
use crate::game::GameState;
use crate::world::tileset::TILE_SIZE;
use wasm_bindgen::JsCast;

pub(crate) fn update(game: &mut Game) {
    let window = match web_sys::window() {
        Some(w) => w,
        None => return,
    };
    let document = match window.document() {
        Some(d) => d,
        None => return,
    };

    // Menu
    if let Some(menu_el) = document.get_element_by_id("menu") {
        if matches!(game.state, GameState::TitleScreen | GameState::DeathScreen | GameState::BonfireMenu | GameState::LevelUpMenu | GameState::TravelMenu) {
            let header = if game.state == GameState::LevelUpMenu {
                format!("<div class=\"menu-item\" style=\"color:#aaa;font-size:16px\">等级 {} · 灵魂: {} · 费用: {}</div>", game.player.level, game.souls, game.player.level_up_cost())
            } else {
                String::new()
            };
            let html: String = game.menu.items.iter().enumerate().map(|(i, item)| {
                let extra = if game.state == GameState::LevelUpMenu && i < 3 {
                    match i {
                        0 => format!(" [{}]", game.player.vigor),
                        1 => format!(" [{}]", game.player.endurance),
                        2 => format!(" [{}]", game.player.strength),
                        _ => String::new(),
                    }
                } else { String::new() };
                if i == game.menu.selected_index {
                    format!("<div class=\"menu-item selected\">▸ {}{}</div>", item.label, extra)
                } else {
                    format!("<div class=\"menu-item\">{}{}</div>", item.label, extra)
                }
            }).collect::<Vec<_>>().join("");
            let _ = menu_el.set_attribute("style", "");
            menu_el.set_inner_html(&format!("{}{}", header, html));
        } else {
            let _ = menu_el.set_attribute("style", "display:none");
            menu_el.set_inner_html("");
        }
    }

    // Death title / Victory title
    if let Some(el) = document.get_element_by_id("death-title") {
        if game.state == GameState::DeathScreen {
            let t = game.death_anim_timer;
            if t > 0.5 {
                let text_alpha = ((t - 0.5) / 1.0).min(1.0);
                let scale = 0.5 + text_alpha * 0.5;
                el.set_text_content(Some("你死了"));
                let _ = el.set_attribute("style", &format!(
                    "opacity: {}; transform: translate(-50%, -50%) scale({:.2});",
                    text_alpha, scale
                ));
            } else {
                el.set_text_content(Some(""));
                let _ = el.set_attribute("style", "opacity: 0;");
            }
        } else if game.state == GameState::Victory {
            let mins = (game.play_time / 60.0) as u32;
            let secs = (game.play_time % 60.0) as u32;
            let bosses_list = game.bosses_defeated.join(", ");
            let ng_label = if game.ng_plus == 0 { String::new() } else { format!("NG+{} ", game.ng_plus) };
            el.set_text_content(Some(&format!(
                "胜利\n\n{}火焰已传承。\n\n已击败Boss: {}\n用时: {}:{:02}\n击杀敌人: {}\n造成伤害: {}\n承受伤害: {}\n死亡次数: {}\n等级: {}\n\n按Enter开始新周目",
                ng_label, bosses_list, mins, secs, game.enemies_killed, game.damage_dealt, game.damage_taken, game.death_count, game.player.level
            )));
            let _ = el.set_attribute("style",
                "color: #e8c840; text-shadow: 0 0 30px rgba(232,200,64,0.8), 0 0 60px rgba(232,200,64,0.3); \
                 white-space: pre-line; letter-spacing: 4px; line-height: 1.6; font-size: 18px;");
        } else {
            let _ = el.set_attribute("style", "display:none");
        }
    }

    // Level-up flash text
    if let Some(el) = document.get_element_by_id("level-up-text") {
        if game.level_up_flash > 0.0 {
            let alpha = (game.level_up_flash / 1.5).min(1.0);
            let _ = el.set_attribute("style", &format!("opacity: {}; color: #e8c840; font-size: 32px; text-shadow: 0 0 20px rgba(232,200,64,0.8); letter-spacing: 8px;", alpha));
            el.set_text_content(Some(&format!("等级 {}", game.player.level)));
        } else {
            let _ = el.set_attribute("style", "display:none");
            el.set_text_content(Some(""));
        }
    }

    // HUD text
    if let Some(el) = document.get_element_by_id("hud-text") {
        let hp = game.player.hp;
        let max_hp = game.player.max_hp;
        let stamina = game.player.stamina.current as i32;
        let max_sta = game.player.stamina.maximum as i32;
        let state_name = match game.player.state {
            EntityState::Idle => "待机",
            EntityState::Moving => "移动",
            EntityState::Attacking => "攻击",
            EntityState::Rolling => "翻滚",
            EntityState::Staggered => "硬直",
            EntityState::Dead => "死亡",
            EntityState::Blocking => "格挡",
        };
        let mut text = format!(
            "HP {}/{} | 精力 {}/{} | 攻击 {} | Lv{} | {} | {}",
            hp, max_hp, stamina, max_sta, game.player.damage(), game.player.level, state_name,
            game.player.weapon.display_name()
        );
        if game.state == GameState::Playing && area_has_bonfire(game.area) {
            let (px, py) = game.player.position();
            let dx = px - game.bonfire_x;
            let dy = py - game.bonfire_y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < 40.0 {
                text.push_str(" | [Enter] 篝火");
            }
            for chest in &game.chests {
                if chest.opened || chest.mimic_revealed { continue; }
                let cdx = px - chest.x;
                let cdy = py - chest.y;
                let cdist = (cdx * cdx + cdy * cdy).sqrt();
                if cdist < 30.0 {
                    text.push_str(" | [Enter] 开启宝箱");
                    break;
                }
            }
            for npc in &game.npcs {
                let ndx = px - npc.x;
                let ndy = py - npc.y;
                let ndist = (ndx * ndx + ndy * ndy).sqrt();
                if ndist < 40.0 {
                    text.push_str(&format!(" | [Enter] 与{}对话", npc.name));
                    break;
                }
            }
        }
        el.set_text_content(Some(&text));
    }

    // Souls + area name
    if let Some(el) = document.get_element_by_id("souls-text") {
        let mut text = format!("{}{} | 灵魂: {} | 原素瓶: {}/{}",
            if game.ng_plus > 0 { format!("NG+{} ", game.ng_plus) } else { String::new() },
            area_name(game.area), game.souls, game.bonfire.estus_charges, game.bonfire.estus_max);
        let has_moss = game.inventory.iter().any(|i| matches!(&i.kind, InventoryItemKind::Consumable(n) if n == "PurpleMoss"));
        let has_bone = game.inventory.iter().any(|i| matches!(&i.kind, InventoryItemKind::Consumable(n) if n == "HomewardBone"));
        if has_moss { text.push_str(" | [Q] 苔藓"); }
        if has_bone { text.push_str(" | [Q] 归骨"); }
        if game.player.poison_timer > 0.0 {
            text.push_str(&format!(" | 中毒 ({:.0}s)", game.player.poison_timer));
        }
        if let Some((ref msg, t)) = game.pickup_notification {
            let alpha = (t / 2.0).min(1.0);
            text.push_str(&format!("<br/><span style='color:#e8c840;opacity:{:.2}'>▲ {}</span>", alpha, msg));
            el.set_inner_html(&text);
        } else {
            el.set_text_content(Some(&text));
        }
        let style = if game.player.poison_timer > 0.0 { "color: #6c6;white-space:pre-line;" } else { "white-space:pre-line;" };
        let _ = el.set_attribute("style", style);
    }

    // Inventory panel — DS3-style tabbed menu
    const INVENTORY_STYLE: &str =
        "display:block; background:rgba(0,0,0,0.92); padding:16px 20px; \
         border:1px solid #444; border-radius:2px; width:380px; \
         position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); \
         font-family:'Segoe UI',Arial,sans-serif;";
    if let Some(el) = document.get_element_by_id("menu") {
        if game.show_inventory && game.menu_dirty {
            let cur = game.menu_cursor;
            let tab = game.menu_tab;

            // Tab bar
            let tabs = [
                ("装备", MenuTab::Equipment),
                ("物品", MenuTab::Items),
                ("参数", MenuTab::Stats),
            ];
            let tab_bar: String = tabs.iter().map(|(name, t)| {
                if *t == tab {
                    format!("<span style='color:#e8c840;font-size:15px;padding:4px 16px;border-bottom:2px solid #e8c840'>{}</span>", name)
                } else {
                    format!("<span style='color:#666;font-size:15px;padding:4px 16px'>{}</span>", name)
                }
            }).collect::<Vec<_>>().join("");

            let mut html = format!(
                "<div style='display:flex;justify-content:center;align-items:center;margin-bottom:12px;border-bottom:1px solid #333;padding-bottom:6px'>{}<span style='color:#555;font-size:11px;margin-left:16px'>←→切换 · ESC关闭</span></div>",
                tab_bar,
            );

            match tab {
                MenuTab::Equipment => {
                    let defense = game.player.equipment.total_defense();
                    let total_weight = game.player.total_weight();
                    let max_load = game.player.max_equip_load();
                    let load_pct = total_weight / max_load * 100.0;
                    let roll_type = if load_pct < 30.0 { "快速" } else if load_pct < 70.0 { "普通" } else { "缓慢" };

                    html.push_str(&format!(
                        "<div style='color:#888;font-size:11px;margin-bottom:8px'>防御 {:.0} · 负重 {:.1}/{} ({:.0}%) · 翻滚 {}</div>",
                        defense, total_weight, max_load, load_pct, roll_type
                    ));

                    let slots: [(&str, String); 8] = [
                        ("右手", format!("{} (攻:{})", game.player.weapon.display_name(), game.player.damage())),
                        ("左手", format!("{}", game.player.equipment.left_hand.active().display_name())),
                        ("头部", format!("{}", if game.player.equipment.head.name == "None" { "—".into() } else { game.player.equipment.head.name.clone() })),
                        ("身体", format!("{}", if game.player.equipment.chest.name == "None" { "—".into() } else { game.player.equipment.chest.name.clone() })),
                        ("手部", format!("{}", if game.player.equipment.hands.name == "None" { "—".into() } else { game.player.equipment.hands.name.clone() })),
                        ("腿部", format!("{}", if game.player.equipment.legs.name == "None" { "—".into() } else { game.player.equipment.legs.name.clone() })),
                        ("戒指1", format!("{}", game.player.equipment.ring_1.as_ref().map_or("—".into(), |r| r.name.clone()))),
                        ("戒指2", format!("{}", game.player.equipment.ring_2.as_ref().map_or("—".into(), |r| r.name.clone()))),
                    ];
                    for (i, (label, value)) in slots.iter().enumerate() {
                        let selected = i == cur;
                        let (col, prefix) = if selected { ("#e8c840", "▸ ") } else { ("#999", "  ") };
                        html.push_str(&format!(
                            "<div style='color:{};font-size:14px;line-height:1.8'>{}{:<4} {}</div>",
                            col, prefix, label, value
                        ));
                    }
                }
                MenuTab::Items => {
                    if game.inventory.is_empty() {
                        html.push_str("<div style='color:#666;font-size:14px;text-align:center;padding:20px'>没有物品</div>");
                    } else {
                        for (i, item) in game.inventory.iter().enumerate() {
                            let selected = i == cur;
                            let (col, prefix) = if selected { ("#e8c840", "▸ ") } else { ("#999", "  ") };
                            let desc = match &item.kind {
                                InventoryItemKind::Consumable(n) if n == "PurpleMoss" => " <span style='color:#6c6;font-size:11px'>[R] 治愈中毒</span>",
                                InventoryItemKind::Consumable(n) if n == "HomewardBone" => " <span style='color:#6c6;font-size:11px'>[R] 传送至篝火</span>",
                                InventoryItemKind::Weapon(_) => " <span style='color:#88f;font-size:11px'>武器</span>",
                                InventoryItemKind::Armor(_, _) => " <span style='color:#f88;font-size:11px'>防具</span>",
                                InventoryItemKind::Ring(_) => " <span style='color:#f8f;font-size:11px'>戒指</span>",
                                _ => "",
                            };
                            html.push_str(&format!(
                                "<div style='color:{};font-size:14px;line-height:1.8'>{}{}{}</div>",
                                col, prefix, item.name, desc
                            ));
                        }
                    }
                }
                MenuTab::Stats => {
                    let damage = game.player.damage();
                    let total_weight = game.player.total_weight();
                    let max_load = game.player.max_equip_load();
                    let defense = game.player.equipment.total_defense();
                    let hp_bonus = game.player.equipment.hp_bonus();
                    let stamina_regen = game.player.equipment.stamina_regen_bonus();
                    let damage_bonus = game.player.equipment.damage_bonus();

                    html.push_str(&format!("<div style='text-align:center;color:#cc9;font-size:15px;margin-bottom:10px'>灵魂: {}</div>", game.souls));

                    let stats = [
                        ("等级", format!("{}", game.player.level)),
                        ("生命力", format!("{} (HP {})", game.player.vigor, game.player.max_hp)),
                        ("持久力", format!("{} (精力 {:.0})", game.player.endurance, game.player.stamina.maximum)),
                        ("力量", format!("{} (攻击 {})", game.player.strength, damage)),
                        ("", String::new()),
                        ("HP", format!("{}/{}", game.player.hp, game.player.max_hp)),
                        ("精力", format!("{:.0}/{:.0}", game.player.stamina.current, game.player.stamina.maximum)),
                        ("", String::new()),
                        ("防御力", format!("{:.0}", defense)),
                        ("负重", format!("{:.1}/{:.0}", total_weight, max_load)),
                        ("攻击力", format!("{}", damage)),
                        ("武器", format!("{}", game.player.weapon.display_name())),
                    ];

                    for (label, value) in &stats {
                        if label.is_empty() {
                            html.push_str("<div style='height:6px'></div>");
                        } else {
                            html.push_str(&format!(
                                "<div style='color:#aaa;font-size:14px;line-height:1.8'>  {:<6} {}</div>",
                                label, value
                            ));
                        }
                    }

                    if hp_bonus > 0.0 { html.push_str(&format!("<div style='color:#6c6;font-size:11px'>  HP加成 +{:.0}%</div>", hp_bonus * 100.0)); }
                    if stamina_regen > 0.0 { html.push_str(&format!("<div style='color:#6c6;font-size:11px'>  精力回复 +{:.0}%</div>", stamina_regen * 100.0)); }
                    if damage_bonus > 0.0 { html.push_str(&format!("<div style='color:#6c6;font-size:11px'>  伤害加成 +{:.0}%</div>", damage_bonus * 100.0)); }
                }
            }

            let _ = el.set_attribute("style", INVENTORY_STYLE);
            el.set_text_content(None);
            el.set_inner_html(&html);
            game.menu_dirty = false;
        } else if game.show_inventory {
            let _ = el.set_attribute("style", INVENTORY_STYLE);
        }
    }

    // Boss name
    if let Some(el) = document.get_element_by_id("boss-name") {
        if let Some(ref boss) = game.boss {
            if !boss.is_dead() && boss.boss_activated {
                if game.boss_intro_timer > 0.0 {
                    let t = game.boss_intro_timer;
                    let alpha = if t > 2.0 {
                        (3.0 - t) / 1.0
                    } else if t > 1.0 {
                        1.0
                    } else {
                        t / 1.0
                    };
                    let _ = el.set_attribute("style", &format!(
                        "font-size: 42px; color: #e8c840; text-shadow: 0 0 30px rgba(232,200,64,0.8); opacity: {}; top: 25%; letter-spacing: 12px;",
                        alpha
                    ));
                    el.set_text_content(Some(&boss.name));
                } else {
                    let _ = el.set_attribute("style", "font-size: 14px; color: #c8c; top: 6px;");
                    el.set_text_content(Some(&format!("{} — HP: {}/{}", boss.name, boss.hp, boss.max_hp)));
                }
            } else {
                let _ = el.set_attribute("style", "display:none");
            }
        } else {
            let _ = el.set_attribute("style", "display:none");
        }
    }

    // NPC dialogue box (dedicated element, separate from boss name)
    if let Some(el) = document.get_element_by_id("npc-dialogue") {
        let talking_npc = game.npcs.iter().find(|n| n.talking);
        if let Some(npc) = talking_npc {
            let line = npc.dialogue.get(npc.dialogue_index).map(|s| s.as_str()).unwrap_or("...");
            el.set_text_content(Some(&format!("{}: {}", npc.name, line)));
            let _ = el.set_attribute("style", "");
        } else {
            let _ = el.set_attribute("style", "display:none");
            el.set_text_content(Some(""));
        }
    }

    // Minimap
    if game.state == GameState::Playing {
        if let Some(minimap_el) = document.get_element_by_id("minimap-canvas") {
            let canvas: web_sys::HtmlCanvasElement = match minimap_el.dyn_into::<web_sys::HtmlCanvasElement>() {
                Ok(c) => c,
                Err(_) => return,
            };
            let ctx = match canvas.get_context("2d").ok().flatten() {
                Some(ctx) => ctx.dyn_into::<web_sys::CanvasRenderingContext2d>().ok(),
                None => None,
            };
            if let Some(ctx) = ctx {
                fn fill_style(ctx: &web_sys::CanvasRenderingContext2d, color: &str) {
                    ctx.set_fill_style_str(color);
                }
                let mm_w = 120.0_f64;
                let mm_h = 120.0_f64;
                let scale_x = mm_w / game.chunk.world_width() as f64;
                let scale_y = mm_h / game.chunk.world_height() as f64;
                let scale = scale_x.min(scale_y);
                let (px, py) = game.player.position();

                ctx.clear_rect(0.0, 0.0, mm_w, mm_h);

                for ty in (0..game.chunk.height).step_by(2) {
                    for tx in (0..game.chunk.width).step_by(2) {
                        let tile = game.chunk.tiles[ty][tx];
                        let color = match tile {
                            crate::world::tileset::TileId::Ground => "#333",
                            crate::world::tileset::TileId::Wall => "#1a1a1a",
                            crate::world::tileset::TileId::Poison => "#2a3a1a",
                            _ => continue,
                        };
                        fill_style(&ctx, color);
                        let mx = tx as f64 * TILE_SIZE as f64 * scale;
                        let my = ty as f64 * TILE_SIZE as f64 * scale;
                        let s = 2.0 * TILE_SIZE as f64 * scale;
                        ctx.fill_rect(mx, my, s, s);
                    }
                }

                fill_style(&ctx, "#c44");
                for enemy in &game.enemies {
                    if enemy.is_dead() { continue; }
                    let (ex, ey) = enemy.position();
                    ctx.begin_path();
                    let _ = ctx.arc(ex as f64 * scale, ey as f64 * scale, 2.0, 0.0, std::f64::consts::TAU);
                    ctx.fill();
                }

                if let Some(ref boss) = game.boss {
                    if !boss.is_dead() {
                        fill_style(&ctx, "#f80");
                        let (bx, by) = boss.position();
                        ctx.begin_path();
                        let _ = ctx.arc(bx as f64 * scale, by as f64 * scale, 3.0, 0.0, std::f64::consts::TAU);
                        ctx.fill();
                    }
                }

                fill_style(&ctx, "#48f");
                for gate in &game.fog_gates {
                    if !gate.active { continue; }
                    let gx = gate.x as f64 * scale;
                    let gy = gate.y as f64 * scale;
                    let gw = gate.w as f64 * scale;
                    let gh = gate.h as f64 * scale;
                    ctx.fill_rect(gx - gw * 0.5, gy - gh * 0.5, gw, gh);
                }

                fill_style(&ctx, "#0f0");
                ctx.begin_path();
                let _ = ctx.arc(px as f64 * scale, py as f64 * scale, 2.5, 0.0, std::f64::consts::TAU);
                ctx.fill();

                if area_has_bonfire(game.area) {
                    fill_style(&ctx, "#e8c840");
                    ctx.begin_path();
                    let _ = ctx.arc(game.bonfire_x as f64 * scale, game.bonfire_y as f64 * scale, 2.0, 0.0, std::f64::consts::TAU);
                    ctx.fill();
                }
            }
        }
    } else if let Some(minimap_el) = document.get_element_by_id("minimap-canvas") {
        let _ = minimap_el.set_attribute("style", "display:none");
    }
}
