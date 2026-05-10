use crate::bridge::wasm_entry::{
    load_area, ArmorSlot, DustParticle, Game, InventoryItem,
    InventoryItemKind, ItemKind, NpcKind,
};
use crate::entity::entity_trait::Entity;

/// Collect an item into the player's inventory, auto-equipping if applicable.
/// Returns a notification string if something was collected.
pub(crate) fn collect_item(game: &mut Game, kind: &ItemKind) -> Option<String> {
    match kind {
        ItemKind::SoulOrb(n) => {
            game.souls += *n;
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some(format!("获得 {} 灵魂", n))
        }
        ItemKind::EstusShard => {
            game.bonfire.estus_max += 1;
            game.bonfire.estus_charges = game.bonfire.estus_max;
            game.audio.play_sfx("estus", 0.1, 0.0);
            Some("获得 原素碎片".into())
        }
        ItemKind::PurpleMoss => {
            game.player.poison_timer = 0.0;
            game.inventory.push(InventoryItem {
                name: "紫苔藓".into(),
                kind: InventoryItemKind::Consumable("PurpleMoss".into()),
            });
            game.audio.play_sfx("estus", 0.08, 0.0);
            Some("获得 紫苔藓".into())
        }
        ItemKind::HomewardBone => {
            game.inventory.push(InventoryItem {
                name: "归还骨片".into(),
                kind: InventoryItemKind::Consumable("HomewardBone".into()),
            });
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some("获得 归还骨片".into())
        }
        ItemKind::WeaponDrop(wt) => {
            let wname = weapon_display_name(wt);
            game.inventory.push(InventoryItem {
                name: wname.into(),
                kind: InventoryItemKind::Weapon(*wt),
            });
            let weapon = create_weapon(wt);
            if game.player.weapon.weapon_type == crate::combat::weapon::WeaponType::Fist {
                game.player.weapon = weapon;
            } else {
                game.player.alt_weapon = Some(weapon);
            }
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some(format!("获得 {}", wname))
        }
        ItemKind::ArmorDrop(slot, name) => {
            game.inventory.push(InventoryItem {
                name: name.clone(),
                kind: InventoryItemKind::Armor(*slot, name.clone()),
            });
            let armor = create_armor(name);
            equip_armor(game, *slot, armor);
            game.player.apply_stats();
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some(format!("获得 {}", name))
        }
        ItemKind::RingDrop(name) => {
            let ring = create_ring(name)?;
            game.inventory.push(InventoryItem {
                name: name.clone(),
                kind: InventoryItemKind::Ring(name.clone()),
            });
            if game.player.equipment.ring_1.is_none() {
                game.player.equipment.ring_1 = Some(ring);
            } else if game.player.equipment.ring_2.is_none() {
                game.player.equipment.ring_2 = Some(ring);
            }
            game.player.apply_stats();
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some(format!("获得 {}", name))
        }
        ItemKind::TitaniteShard => {
            game.inventory.push(InventoryItem {
                name: "楔形石碎片".into(),
                kind: InventoryItemKind::Consumable("TitaniteShard".into()),
            });
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some("获得 楔形石碎片".into())
        }
        ItemKind::Firebomb => {
            game.inventory.push(InventoryItem {
                name: "火焰壶".into(),
                kind: InventoryItemKind::Consumable("Firebomb".into()),
            });
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some("获得 火焰壶".into())
        }
        ItemKind::Ember => {
            game.inventory.push(InventoryItem {
                name: "余火".into(),
                kind: InventoryItemKind::Consumable("Ember".into()),
            });
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some("获得 余火".into())
        }
        ItemKind::UndeadBoneShard => {
            game.inventory.push(InventoryItem {
                name: "不死者的遗骨".into(),
                kind: InventoryItemKind::Consumable("UndeadBoneShard".into()),
            });
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some("获得 不死者的遗骨".into())
        }
        ItemKind::Consumable(name) => {
            game.inventory.push(InventoryItem {
                name: name.clone(),
                kind: InventoryItemKind::Consumable(name.clone()),
            });
            game.audio.play_sfx("souls", 0.08, 0.0);
            Some(format!("获得 {}", name))
        }
    }
}

fn weapon_display_name(wt: &crate::combat::weapon::WeaponType) -> &'static str {
    use crate::combat::weapon::WeaponType;
    match wt {
        WeaponType::GreatAxe => "大斧",
        WeaponType::Dagger => "匕首",
        WeaponType::Spear => "长枪",
        WeaponType::Uchigatana => "打刀",
        WeaponType::Shield => "盾牌",
        _ => "长剑",
    }
}

fn create_weapon(wt: &crate::combat::weapon::WeaponType) -> crate::combat::weapon::Weapon {
    use crate::combat::weapon::WeaponType;
    match wt {
        WeaponType::GreatAxe => crate::combat::weapon::Weapon::great_axe(),
        WeaponType::Dagger => crate::combat::weapon::Weapon::dagger(),
        WeaponType::Spear => crate::combat::weapon::Weapon::spear(),
        WeaponType::Uchigatana => crate::combat::weapon::Weapon::uchigatana(),
        _ => crate::combat::weapon::Weapon::longsword(),
    }
}

fn create_armor(name: &str) -> crate::rpg::equipment::ArmorPiece {
    match name {
        "Hollow Soldier Helm" => crate::rpg::equipment::ArmorPiece::hollow_soldier_helm(),
        "Hollow Soldier Armor" => crate::rpg::equipment::ArmorPiece::hollow_soldier_chest(),
        "Knight Helm" => crate::rpg::equipment::ArmorPiece::knight_helm(),
        "Knight Armor" => crate::rpg::equipment::ArmorPiece::knight_chest(),
        _ => crate::rpg::equipment::ArmorPiece::none(),
    }
}

fn equip_armor(game: &mut Game, slot: ArmorSlot, armor: crate::rpg::equipment::ArmorPiece) {
    match slot {
        ArmorSlot::Head => game.player.equipment.head = armor,
        ArmorSlot::Chest => game.player.equipment.chest = armor,
        ArmorSlot::Legs => game.player.equipment.legs = armor,
        ArmorSlot::Hands => game.player.equipment.hands = armor,
    }
}

fn create_ring(name: &str) -> Option<crate::rpg::equipment::Ring> {
    match name {
        "Life Ring" => Some(crate::rpg::equipment::Ring::life_ring()),
        "Chloranthy Ring" => Some(crate::rpg::equipment::Ring::chloranthy()),
        "Ring of the Lion" => Some(crate::rpg::equipment::Ring::lion_ring()),
        _ => None,
    }
}

/// Spawn collection particles at a position.
pub(crate) fn spawn_collection_particles(game: &mut Game, x: f32, y: f32) {
    for i in 0..8 {
        let angle = i as f32 * std::f32::consts::TAU / 8.0;
        game.dust_particles.push(DustParticle {
            x,
            y,
            vx: angle.cos() * 60.0,
            vy: angle.sin() * 60.0,
            timer: 0.4,
        });
    }
}

/// Tick fog gate collision, item pickup, chest/NPC/bonfire/bloodstain interactions.
/// Returns true if an area transition happened (caller should return early).
pub(crate) fn tick_interactions(game: &mut Game, interact: bool) -> bool {
    let (px, py) = game.player.position();

    // Fog gate collision
    {
        let mut boss_spawn = None;
        let mut area_transition = None;
        for gate in &game.fog_gates {
            if !gate.active { continue; }
            let in_x = px > gate.x - gate.w * 0.5 && px < gate.x + gate.w * 0.5;
            let in_y = py > gate.y - gate.h * 0.5 && py < gate.y + gate.h * 0.5;
            if in_x && in_y {
                if gate.destination == game.area {
                    boss_spawn = Some((gate.dest_x, gate.dest_y));
                } else {
                    area_transition = Some((gate.destination, gate.dest_x, gate.dest_y));
                }
                break;
            }
        }
        if let Some((bx, by)) = boss_spawn {
            game.player.transform.x = bx;
            game.player.transform.y = by;
            game.camera.x = bx;
            game.camera.y = by;
            if let Some(ref mut boss) = game.boss {
                if !boss.boss_activated && !boss.is_dead() {
                    boss.boss_activated = true;
                    game.boss_active = true;
                    game.boss_intro_timer = 3.0;
                    game.state_timer = 0.0;
                }
            }
        }
        if let Some((dest_area, dx, dy)) = area_transition {
            if game.state_timer < 0.5 { return false; }
            load_area(game, dest_area);
            game.player.transform.x = dx;
            game.player.transform.y = dy;
            game.camera.x = dx;
            game.camera.y = dy;
            game.player.invuln_timer = 2.0;
            let heal = (game.player.max_hp as f32 * 0.3) as i32;
            game.player.hp = (game.player.hp + heal).min(game.player.max_hp);
            return true;
        }
    }

    // Bloodstain soul retrieval
    if game.has_bloodstain {
        let dx = px - game.bloodstain_x;
        let dy = py - game.bloodstain_y;
        let dist = (dx * dx + dy * dy).sqrt();
        if dist < 24.0 {
            game.souls += game.bloodstain_souls;
            game.has_bloodstain = false;
            game.audio.play_sfx("souls", 0.08, 0.0);
        }
    }

    // Item pickup (auto-collect on proximity)
    let (px, py) = game.player.position();
    let pickups: Vec<(usize, f32, f32, ItemKind)> = game.items.iter().enumerate()
        .filter(|(_, item)| !item.collected)
        .filter_map(|(i, item)| {
            let dx = px - item.x;
            let dy = py - item.y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < 30.0 { Some((i, item.x, item.y, item.kind.clone())) } else { None }
        })
        .collect();
    for (idx, ix, iy, kind) in pickups {
        game.items[idx].collected = true;
        spawn_collection_particles(game, ix, iy);
        if let Some(msg) = collect_item(game, &kind) {
            game.pickup_notification = Some((msg, 2.0));
        }
    }

    // Chest interaction
    if interact {
        let chest_hit: Option<(usize, f32, f32, bool, ItemKind)> = game.chests.iter().enumerate()
            .filter(|(_, c)| !c.opened && !c.mimic_revealed)
            .filter_map(|(i, c)| {
                let dx = px - c.x;
                let dy = py - c.y;
                let dist = (dx * dx + dy * dy).sqrt();
                if dist < 30.0 { Some((i, c.x, c.y, c.is_mimic, c.loot.clone())) } else { None }
            })
            .next();
        if let Some((idx, cx, cy, is_mimic, loot)) = chest_hit {
            if is_mimic {
                game.chests[idx].mimic_revealed = true;
                game.camera.add_shake(6.0);
                game.audio.play_sfx("boss_die", 0.2, 0.0);
                game.pickup_notification = Some(("宝箱怪!".into(), 2.0));
                let mimic_id = game.enemies.len() as u64 + 100;
                game.enemies.push(crate::entity::enemy::Enemy::new_mimic(mimic_id, cx, cy));
                if let Some(mimic) = game.enemies.last_mut() {
                    mimic.mimic_activated = true;
                    mimic.aggro.check_detection(mimic.transform.x, mimic.transform.y, 1, px, py);
                }
            } else {
                game.chests[idx].opened = true;
                if let Some(msg) = collect_item(game, &loot) {
                    game.pickup_notification = Some((msg, 2.0));
                }
                game.camera.add_shake(2.0);
            }
        }
    }

    // NPC dialogue interaction
    let any_npc_talking = game.npcs.iter().any(|n| n.talking);
    if any_npc_talking {
        if interact {
            for npc in &mut game.npcs {
                if npc.talking {
                    npc.dialogue_index += 1;
                    if npc.dialogue_index >= npc.dialogue.len() {
                        npc.talking = false;
                        npc.dialogue_index = 0;
                    } else if npc.dialogue_index == npc.dialogue.len() - 1 {
                        match npc.kind {
                            NpcKind::LevelUp => {
                                let cost = game.player.level_up_cost();
                                if game.souls >= cost as u32 {
                                    game.souls -= cost as u32;
                                    game.player.level += 1;
                                    game.player.strength += 1;
                                    game.player.apply_stats();
                                    game.level_up_flash = 0.5;
                                }
                            }
                            NpcKind::Merchant => {
                                if game.souls >= 500 {
                                    game.souls -= 500;
                                    game.bonfire.estus_max += 1;
                                    game.bonfire.estus_charges = game.bonfire.estus_max;
                                }
                            }
                            NpcKind::Blacksmith => {
                                if game.souls >= 1000 {
                                    game.souls -= 1000;
                                    game.player.weapon.base_damage += 15;
                                    if let Some(ref mut alt) = game.player.alt_weapon {
                                        alt.base_damage += 15;
                                    }
                                }
                            }
                            NpcKind::Dialogue => {}
                        }
                    }
                    break;
                }
            }
        }
    } else if interact {
        for npc in &mut game.npcs {
            let dx = px - npc.x;
            let dy = py - npc.y;
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < 40.0 {
                npc.talking = true;
                npc.dialogue_index = 0;
                break;
            }
        }
    }

    false
}
