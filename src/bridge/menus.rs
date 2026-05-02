use crate::bridge::wasm_entry::{
    area_from_str, load_area, AreaId, Game,
};
use crate::entity::entity_trait::{Entity, EntityState};
use crate::entity::player::Player;
use crate::game::{GameState, MenuAction, MenuState};
use crate::save::bonfire::BonfireState;
use crate::save::save_manager::{self, SaveData};

/// Apply menu navigation from keyboard and gamepad.
macro_rules! navigate_menu {
    ($game:expr) => {
        if $game.input.menu_up() { $game.menu.move_up(); }
        if $game.input.menu_down() { $game.menu.move_down(); }
    };
}

pub(crate) fn update_title_screen(game: &mut Game) {
    if game.input.confirm_pressed() {
        if let Some(action) = game.menu.current_action() {
            match action {
                MenuAction::NewGame => {
                    game.player = Player::new(1, 320.0, 320.0);
                    game.boss_defeated = false;
                    game.souls = 0;
                    game.bonfire = BonfireState::new();
                    game.enemies_killed = 0;
                    game.damage_dealt = 0;
                    game.damage_taken = 0;
                    game.death_count = 0;
                    game.play_time = 0.0;
                    game.bosses_defeated = vec![];
                    game.inventory = vec![];
                    game.has_bloodstain = false;
                    game.bloodstain_souls = 0;
                    load_area(game, AreaId::CemeteryOfAsh);
                }
                MenuAction::Continue => {
                    if let Some(save) = save_manager::load_from_localstorage() {
                        game.player.level = save.player_level;
                        game.player.vigor = save.vigor;
                        game.player.endurance = save.endurance;
                        game.player.strength = save.strength;
                        game.player.apply_stats();
                        game.player.hp = save.player_hp;
                        game.player.weapon.base_damage = save.weapon_damage;
                        if let (Some(_), Some(dmg)) = (save.alt_weapon_name.as_ref(), save.alt_weapon_damage) {
                            if let Some(ref mut alt) = game.player.alt_weapon {
                                alt.base_damage = dmg;
                            }
                        }
                        game.souls = save.souls;
                        game.bonfire = save.bonfire.clone();
                        game.enemies_killed = save.enemies_killed;
                        game.play_time = save.play_time;
                        game.death_count = save.death_count;
                        game.damage_dealt = save.damage_dealt;
                        game.damage_taken = save.damage_taken;
                        game.bosses_defeated = save.bosses_defeated.clone();
                        let saved_area = area_from_str(&save.current_room);
                        load_area(game, saved_area);
                        game.player.transform.x = save.player_x;
                        game.player.transform.y = save.player_y;
                        game.player.hp = save.player_hp;
                        game.camera.x = save.player_x;
                        game.camera.y = save.player_y;
                    }
                    game.state = GameState::Playing;
                    game.time.accumulator = 0.0;
                    game.state_timer = 0.0;
                }
                _ => {}
            }
        }
    }
    navigate_menu!(game);
}

pub(crate) fn update_death(game: &mut Game) {
    game.death_anim_timer += crate::core::time::FIXED_DT as f32;
    if game.death_anim_timer < 2.5 {
        return;
    }
    if game.input.confirm_pressed() {
        if let Some(action) = game.menu.current_action() {
            match action {
                MenuAction::Continue => {
                    game.souls = 0;
                    game.bonfire.rest();
                    game.bonfire.estus_charges = game.bonfire.estus_max;
                    let current_area = game.area;
                    load_area(game, current_area);
                    game.player.hp = game.player.max_hp;
                    game.player.state = EntityState::Idle;
                    game.time.accumulator = 0.0;
                    game.state_timer = 0.0;
                    game.death_anim_timer = 0.0;
                    game.state = GameState::Playing;
                }
                MenuAction::QuitToTitle => {
                    game.state = GameState::TitleScreen;
                    game.menu = MenuState::title_screen_with_save_check();
                }
                _ => {}
            }
        }
    }
    navigate_menu!(game);
}

pub(crate) fn update_bonfire_menu(game: &mut Game) {
    if game.input.cancel_pressed() {
        game.state = GameState::Playing;
        return;
    }
    if game.input.confirm_pressed() {
        if let Some(action) = game.menu.current_action().cloned() {
            match action {
                MenuAction::Rest => {
                    game.bonfire.rest();
                    game.player.hp = game.player.max_hp;
                    game.bonfire.estus_charges = game.bonfire.estus_max;
                    game.player.stamina.current = game.player.stamina.maximum;
                    game.player.poison_timer = 0.0;
                    let current_area = game.area;
                    load_area(game, current_area);
                    game.player.hp = game.player.max_hp;
                    let (px, py) = game.player.position();
                    let save = SaveData {
                        player_level: game.player.level,
                        vigor: game.player.vigor,
                        endurance: game.player.endurance,
                        strength: game.player.strength,
                        souls: game.souls,
                        bonfire: game.bonfire.clone(),
                        current_room: format!("{:?}", game.area),
                        player_hp: game.player.hp,
                        player_x: px,
                        player_y: py,
                        weapon_name: game.player.weapon.name.clone(),
                        weapon_damage: game.player.weapon.base_damage,
                        alt_weapon_name: game.player.alt_weapon.as_ref().map(|w| w.name.clone()),
                        alt_weapon_damage: game.player.alt_weapon.as_ref().map(|w| w.base_damage),
                        bosses_defeated: game.bosses_defeated.clone(),
                        enemies_killed: game.enemies_killed,
                        items_collected: game.items.iter().filter(|i| i.collected).map(|_| "item".into()).collect(),
                        chests_opened: game.chests.iter().filter(|c| c.opened || c.mimic_revealed).map(|_| "chest".into()).collect(),
                        play_time: game.play_time,
                        death_count: game.death_count,
                        damage_dealt: game.damage_dealt,
                        damage_taken: game.damage_taken,
                    };
                    save_manager::save_to_localstorage(&save);
                }
                MenuAction::LevelUp => {
                    game.state = GameState::LevelUpMenu;
                    game.menu = MenuState::level_up_menu();
                }
                MenuAction::Resume => {
                    game.state = GameState::Playing;
                }
                MenuAction::Travel => {
                    game.state = GameState::TravelMenu;
                    game.menu = MenuState::travel_menu();
                }
                _ => {}
            }
        }
    }
    navigate_menu!(game);
}

pub(crate) fn update_level_up_menu(game: &mut Game) {
    if game.input.cancel_pressed() {
        game.state = GameState::BonfireMenu;
        game.menu = MenuState::bonfire_menu();
        return;
    }
    if game.input.confirm_pressed() {
        let cost = game.player.level_up_cost();
        if game.souls >= cost {
            let idx = game.menu.selected_index;
            match idx {
                0 => { game.player.vigor += 1; game.souls -= cost; game.player.level += 1; game.player.apply_stats(); game.player.hp = game.player.max_hp; game.level_up_flash = 1.5; }
                1 => { game.player.endurance += 1; game.souls -= cost; game.player.level += 1; game.player.apply_stats(); game.level_up_flash = 1.5; }
                2 => { game.player.strength += 1; game.souls -= cost; game.player.level += 1; game.player.apply_stats(); game.level_up_flash = 1.5; }
                3 => { game.state = GameState::BonfireMenu; game.menu = MenuState::bonfire_menu(); }
                _ => {}
            }
        }
    }
    navigate_menu!(game);
}

pub(crate) fn update_travel_menu(game: &mut Game) {
    if game.input.cancel_pressed() {
        game.state = GameState::BonfireMenu;
        game.menu = MenuState::bonfire_menu();
        return;
    }
    navigate_menu!(game);
    if game.input.confirm_pressed() {
        let idx = game.menu.selected_index;
        let areas = [AreaId::FirelinkShrine, AreaId::LothricWall, AreaId::UndeadSettlement, AreaId::CathedralDeep, AreaId::Irithyll];
        if idx < 5 {
            load_area(game, areas[idx]);
        } else {
            game.state = GameState::BonfireMenu;
            game.menu = MenuState::bonfire_menu();
        }
    }
}

pub(crate) fn update_victory(game: &mut Game) {
    if game.input.confirm_pressed() {
        game.ng_plus += 1;
        game.player.hp = game.player.max_hp;
        game.boss_defeated = false;
        game.boss_active = false;
        game.boss = None;
        game.souls = 0;
        game.bosses_defeated = vec![];
        game.enemies_killed = 0;
        game.damage_dealt = 0;
        game.damage_taken = 0;
        game.death_count = 0;
        game.play_time = 0.0;
        game.inventory = vec![];
        game.has_bloodstain = false;
        game.bloodstain_souls = 0;
        game.time.accumulator = 0.0;
        game.state_timer = 0.0;
        load_area(game, AreaId::FirelinkShrine);
        game.state = GameState::Playing;
    }
}
