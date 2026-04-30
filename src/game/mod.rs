#[derive(Clone, Copy, Debug, PartialEq)]
pub enum GameState {
    TitleScreen,
    Playing,
    Paused,
    BonfireMenu,
    LevelUpMenu,
    TravelMenu,
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
                label: "新游戏".into(),
                action: MenuAction::NewGame,
            },
        ];
        if has_save {
            items.push(MenuItem {
                label: "继续游戏".into(),
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
                    label: "生命力 (+HP)".into(),
                    action: MenuAction::LevelUp,
                },
                MenuItem {
                    label: "持久力 (+精力)".into(),
                    action: MenuAction::LevelUp,
                },
                MenuItem {
                    label: "力量 (+攻击)".into(),
                    action: MenuAction::LevelUp,
                },
                MenuItem {
                    label: "返回".into(),
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
                    label: "休息".into(),
                    action: MenuAction::Rest,
                },
                MenuItem {
                    label: "升级".into(),
                    action: MenuAction::LevelUp,
                },
                MenuItem {
                    label: "传送".into(),
                    action: MenuAction::Travel,
                },
                MenuItem {
                    label: "返回".into(),
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
                    label: "在篝火处复活".into(),
                    action: MenuAction::Continue,
                },
                MenuItem {
                    label: "返回标题".into(),
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

    pub fn travel_menu() -> Self {
        Self {
            current: GameState::TravelMenu,
            selected_index: 0,
            items: vec![
                MenuItem { label: "传火祭祀场".into(), action: MenuAction::Travel },
                MenuItem { label: "不死聚落".into(), action: MenuAction::Travel },
                MenuItem { label: "幽邃教堂".into(), action: MenuAction::Travel },
                MenuItem { label: "冷冽谷的伊鲁席尔".into(), action: MenuAction::Travel },
                MenuItem { label: "返回".into(), action: MenuAction::Resume },
            ],
        }
    }

    pub fn current_action(&self) -> Option<&MenuAction> {
        self.items.get(self.selected_index).map(|i| &i.action)
    }
}
