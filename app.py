import os
import json
from textual.app import App
from textual.binding import Binding

from api_client import APIClient
from screens import LoginScreen, AIConfigScreen, GameScreen, NameChangeScreen, CharacterSelectScreen


class DeepIdleApp(App):
    TITLE = "DEEPIDLE - Terminal GUI"
    CSS = """
/* Roguelike RPG styled TUI */
#login-container, #config-container, #name-container {
    display: block;
    align: center middle;
    height: 100%;
    background: #0a0a0f;
    padding: 2;
}
#config-container {
    width: 60;
    height: auto;
}
#login-title {
    content-align: center middle;
    width: 100%;
    text-style: bold;
    color: #ffd27a;
    margin-bottom: 1;
}
#config-title, #name-title {
    content-align: center middle;
    width: 100%;
    text-style: bold;
    color: #ffd27a;
    margin-bottom: 1;
}
Input, Select {
    width: 100%;
    margin-bottom: 1;
}
#config-buttons, #login-buttons {
    width: 100%;
    align: center middle;
    margin-top: 1;
}
Button {
    margin: 0 1;
}
#config-feedback {
    margin-top: 1;
    text-align: center;
}

/* Game Screen Styles */
#control-bar {
    height: 3;
    background: #0a0a0f;
    padding: 0 1;
    align: left middle;
}
#control-bar Button {
    margin-right: 1;
}
#ai-status {
    margin-left: 2;
}

#game-main-container {
    height: 1fr;
}
#left-pane {
    width: 38;
    height: 100%;
    layout: vertical;
}
ObjectivePanel {
    height: 1fr;
}
InventoryPanel {
    height: 18;
}
#objectives {
    padding: 0 1;
}
#slots-container {
    height: 1fr;
    layout: vertical;
}
InventorySlot {
    height: 3;
    margin: 0 1;
}
InventorySlot.empty {
    opacity: 0.5;
}
ActionLog, ThoughtLog {
    height: 1fr;
    max-height: 1fr;
    background: #141420;
    color: #87ceeb;
    overflow-x: hidden;
}
#action-display {
    height: 16;
}
#action-display > #animation-container {
    align: center middle;
    height: 1fr;
}
#action-animation {
    align: center middle;
    width: 100%;
}
#action-name {
    content-align: center middle;
    margin: 0;
}
#action-zone {
    content-align: center middle;
    display: none;
    margin: 0;
}
#action-title {
    margin: 0;
}
#right-pane {
    layout: vertical;
}
#thought-log {
    height: 1fr;
}
#intent-bar {
    height: 3;
    align: center middle;
}
#intent-bar Input {
    width: 1fr;
    margin: 0;
}
#intent-bar Button {
    margin: 0 0 0 1;
}
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+n", "change_name", "Change Name", show=True),
        Binding("ctrl+s", "config_ai", "AI Config", show=True),
    ]

    def action_config_ai(self):
        self.push_screen(AIConfigScreen())

    def action_change_name(self):
        self.push_screen(NameChangeScreen())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = APIClient(source="TUI-GUI")
        self.user_data = None
        self.ai_config = self.load_config()

    def refresh_ui(self):
        self.pop_screen()
        self.push_screen(GameScreen())

    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"provider": "openai", "api_key": "", "model": "gpt-4o", "language": "Thai", "api_base": ""}

    def save_config(self):
        try:
            with open("config.json", "w") as f:
                json.dump(self.ai_config, f)
        except Exception:
            pass

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())

    def on_login_success(self, data):
        self.user_data = data
        characters = data.get("characters", [])
        if len(characters) >= 1:
            self.push_screen(CharacterSelectScreen(characters))
        else:
            self.push_screen(GameScreen())


if __name__ == "__main__":
    app = DeepIdleApp()
    app.run()
