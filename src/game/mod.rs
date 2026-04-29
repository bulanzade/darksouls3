#[derive(Clone, Copy, Debug, PartialEq)]
pub enum GameState {
    TitleScreen,
    Playing,
    Paused,
    BonfireMenu,
    LevelUpMenu,
    DeathScreen,
    GameOver,
    Victory,
}

#[derive(Clone, Debug)]
pub struct MenuState {
    pub current: GameState,
    pub selected_index: usize,
    pub items: Vec<MenuItem>,
}

#[derive(Clone, Debug)]
pub struct MenuItem {
    pub label: String,
    pub action: MenuAction,
}

#[derive(Clone, Debug)]
pub enum MenuAction {
    NewGame,
    Continue,
    Rest,
    LevelUp,
    Travel,
    Resume,
    QuitToTitle,
}

impl MenuState {
    pub fn title_screen() -> Self {
        Self {
            current: GameState::TitleScreen,
            selected_index: 0,
            items: vec![
                MenuItem {
                    label: "New Game".into(),
                    action: MenuAction::NewGame,
                },
                MenuItem {
                    label: "Continue".into(),
                    action: MenuAction::Continue,
                },
            ],
        }
    }

    pub fn title_screen_with_save_check() -> Self {
        let has_save = crate::save::save_manager::has_save();
        let mut items = vec![
            MenuItem {
                label: "New Game".into(),
                action: MenuAction::NewGame,
            },
        ];
        if has_save {
            items.push(MenuItem {
                label: "Continue".into(),
                action: MenuAction::Continue,
            });
        }
        Self {
            current: GameState::TitleScreen,
            selected_index: 0,
            items,
        }
    }

    pub fn level_up_menu() -> Self {
        Self {
            current: GameState::LevelUpMenu,
            selected_index: 0,
            items: vec![
                MenuItem {
                    label: "Vigor (+HP)".into(),
                    action: MenuAction::LevelUp,
                },
                MenuItem {
                    label: "Endurance (+STA)".into(),
                    action: MenuAction::LevelUp,
                },
                MenuItem {
                    label: "Strength (+DMG)".into(),
                    action: MenuAction::LevelUp,
                },
                MenuItem {
                    label: "Back".into(),
                    action: MenuAction::Resume,
                },
            ],
        }
    }

    pub fn bonfire_menu() -> Self {
        Self {
            current: GameState::BonfireMenu,
            selected_index: 0,
            items: vec![
                MenuItem {
                    label: "Rest".into(),
                    action: MenuAction::Rest,
                },
                MenuItem {
                    label: "Level Up".into(),
                    action: MenuAction::LevelUp,
                },
                MenuItem {
                    label: "Travel".into(),
                    action: MenuAction::Travel,
                },
                MenuItem {
                    label: "Resume".into(),
                    action: MenuAction::Resume,
                },
            ],
        }
    }

    pub fn death_screen() -> Self {
        Self {
            current: GameState::DeathScreen,
            selected_index: 0,
            items: vec![
                MenuItem {
                    label: "Respawn at Bonfire".into(),
                    action: MenuAction::Continue,
                },
                MenuItem {
                    label: "Quit to Title".into(),
                    action: MenuAction::QuitToTitle,
                },
            ],
        }
    }

    pub fn move_up(&mut self) {
        if self.selected_index > 0 {
            self.selected_index -= 1;
        }
    }

    pub fn move_down(&mut self) {
        if self.selected_index < self.items.len() - 1 {
            self.selected_index += 1;
        }
    }

    pub fn current_action(&self) -> Option<&MenuAction> {
        self.items.get(self.selected_index).map(|i| &i.action)
    }
}
