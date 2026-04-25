from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Input, Button, Label, Static
from textual.screen import Screen
from textual.message import Message

from constants import TRANSLATIONS, PROVIDERS


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        with Vertical(id="login-container"):
            yield Label("DEEPIDLE", id="login-title")
            yield Label("Please Login or Signup")
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", password=True, id="password")
            with Horizontal(id="login-buttons"):
                yield Button("Login", variant="primary", id="btn-login")
                yield Button("Signup", variant="default", id="btn-signup")
            yield Label("", id="login-error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        username = self.query_one("#username", Input).value
        password = self.query_one("#password", Input).value
        error_label = self.query_one("#login-error", Label)

        if event.button.id == "btn-login":
            data = self.app.api.login(username, password)
            if data:
                self.app.on_login_success(data)
            else:
                error_label.update("[red]Invalid credentials[/red]")
        elif event.button.id == "btn-signup":
            if len(username) < 3:
                error_label.update("[red]Username must be at least 3 characters[/red]")
                return
            data = self.app.api.signup(username, password, username)
            if data:
                error_label.update("[green]Account created! Now login.[/green]")
            else:
                error_label.update("[red]Signup failed[/red]")


class AIConfigScreen(Screen):
    def compose(self) -> ComposeResult:
        with Vertical(id="config-container"):
            yield Label("🤖 LLM Configuration", id="config-title")
            
            yield Label("Provider")
            yield Select(
                [(v["name"], k) for k, v in PROVIDERS.items()],
                value=self.app.ai_config.get("provider", "openai"),
                id="select-provider"
            )
            
            yield Label("API Key")
            yield Input(
                value=self.app.ai_config.get("api_key", ""),
                placeholder="sk-...",
                id="input-apikey",
                password=True
            )
            
            yield Label("Model")
            yield Select(
                [(m, m) for m in PROVIDERS.get("openai", {}).get("models", ["gpt-4o"])],
                id="select-model"
            )
            
            yield Label("Language")
            yield Select(
                [("Thai", "Thai"), ("English", "English")],
                value=self.app.ai_config.get("language", "Thai"),
                id="select-lang"
            )
            
            yield Label("(Optional) Custom API Base")
            yield Input(
                value=self.app.ai_config.get("api_base", ""),
                placeholder="Leave empty for default",
                id="input-apibase"
            )
            
            yield Label("(Optional) Custom Objective")
            yield Input(
                value=self.app.ai_config.get("custom_objective", ""),
                placeholder="E.g., Focus on upgrading wooden_axe only",
                id="input-objective"
            )
            yield Label("AI will prioritize this objective when making decisions", id="objective-hint")

            with Horizontal(id="config-buttons"):
                yield Button("Save", variant="primary", id="btn-save-config")
                yield Button("Test", variant="default", id="btn-test-llm")
            
            yield Label("", id="config-feedback")

    def on_mount(self) -> None:
        self.populate_models()
    
    def populate_models(self):
        provider = self.query_one("#select-provider", Select).value
        models = PROVIDERS.get(provider, {}).get("models", [])
        default_model = PROVIDERS.get(provider, {}).get("default_model", "")
        current = self.app.ai_config.get("model", default_model)
        
        model_select = self.query_one("#select-model", Select)
        options = [(m, m) for m in models]
        model_select.set_options(options)
        if current in models:
            model_select.value = current
        elif models:
            model_select.value = models[0]
        else:
            model_select.value = ""

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.control.id == "select-provider":
            self.populate_models()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save-config":
            provider = self.query_one("#select-provider", Select).value
            self.app.ai_config = {
                "provider": provider,
                "api_key": self.query_one("#input-apikey", Input).value,
                "model": self.query_one("#select-model", Select).value or PROVIDERS.get(provider, {}).get("default_model", "gpt-4o"),
                "language": self.query_one("#select-lang", Select).value,
                "api_base": self.query_one("#input-apibase", Input).value,
                "custom_objective": self.query_one("#input-objective", Input).value,
            }
            self.app.save_config()
            self.app.pop_screen()
        elif event.button.id == "btn-test-llm":
            import threading
            def test():
                try:
                    import litellm
                    api_key = self.query_one("#input-apikey", Input).value
                    model = self.query_one("#select-model", Select).value
                    api_base = self.query_one("#input-apibase", Input).value
                    
                    kwargs = {"model": model, "messages": [{"role": "user", "content": "Hi"}], "api_key": api_key}
                    if api_base:
                        kwargs["api_base"] = api_base
                    
                    response = litellm.completion(**kwargs)
                    self.app.call_from_thread(lambda: self.query_one("#config-feedback", Label).update(f"[green]✔ Success! Response: {response.choices[0].message.content[:50]}...[/green]"))
                except Exception as e:
                    self.app.call_from_thread(lambda: self.query_one("#config-feedback", Label).update(f"[red]✘ Error: {str(e)[:100]}[/red]"))
            
            self.query_one("#config-feedback", Label).update("[dim]Testing...[/dim]")
            threading.Thread(target=test, daemon=True).start()


class GameScreen(Screen):
    def compose(self) -> ComposeResult:
        t = TRANSLATIONS[self.app.ai_config.get("language", "Thai")]
        yield Header()
        with Horizontal(id="control-bar"):
            yield Button(t["play_ai"], variant="success", id="btn-play-ai")
            yield Button(t["stop_ai"], variant="error", id="btn-stop-ai")
            yield Button(t["config"], id="btn-config-ai")
            yield Label(t["status_stopped"], id="ai-status")
        
        with Horizontal(id="game-main-container"):
            with Vertical(id="left-pane"):
                yield ObjectivePanel(id="objectives")
                yield InventoryPanel(id="inventory")
            
            with Vertical(id="center-pane"):
                yield Label(t["action_feed"], classes="pane-title")
                yield ActionAnimation(id="action-display")
                yield GameMapPanel(id="game-map")
                
            with Vertical(id="right-pane"):
                yield Label("═══ AI THOUGHTS ═══", classes="pane-title")
                yield ThoughtLog(id="thought-log")
                with Horizontal(id="intent-bar"):
                    yield Input(placeholder="Tell AI your intent...", id="player-intent")
                    yield Button("Send", variant="primary", id="btn-send-intent")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_data()
        self.refresh_task = asyncio.create_task(self.refresh_loop())
        self.action_display = self.query_one("#action-display", ActionAnimation)
        self.game_map = self.query_one("#game-map", GameMapPanel)
        self.thought_log = self.query_one("#thought-log", ThoughtLog)
        self.ai_process = None
        self._ai_objective = ""
        self._ai_progress = ""
        self._map_visible = True
        
        self.action_display.set_action("idle")
        self.game_map.update_player_position("idle")
        self.thought_log.write("AI Logic Initialized...\n")
        
        self.watch_screen_size()

    def watch_screen_size(self):
        def check_size():
            try:
                container = self.query_one("#game-main-container")
                width = container.size.width if hasattr(container, 'size') else 100
                if width < 80:
                    if self._map_visible or not self.game_map.has_class("hidden"):
                        self.game_map.add_class("hidden")
                        self.game_map.remove_class("compact")
                        self.game_map.set_compact(False)
                        self._map_visible = False
                elif width < 100:
                    if not self._map_visible:
                        self.game_map.remove_class("hidden")
                        self.game_map.add_class("compact")
                        self.game_map.set_compact(True)
                        self._map_visible = True
                    elif not self.game_map.has_class("compact"):
                        self.game_map.add_class("compact")
                        self.game_map.set_compact(True)
                else:
                    if not self._map_visible or self.game_map.has_class("compact"):
                        self.game_map.remove_class("hidden")
                        self.game_map.remove_class("compact")
                        self.game_map.set_compact(False)
                        self._map_visible = True
            except Exception:
                pass
            self.set_timer(0.5, check_size)
        check_size()

    def on_unmount(self) -> None:
        self.stop_ai()
        if hasattr(self, "refresh_task"):
            self.refresh_task.cancel()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-play-ai":
            self.start_ai()
        elif event.button.id == "btn-stop-ai":
            self.stop_ai()
        elif event.button.id == "btn-config-ai":
            self.app.push_screen(AIConfigScreen())
        elif event.button.id == "btn-send-intent":
            self.send_player_intent()

    def send_player_intent(self) -> None:
        intent_input = self.query_one("#player-intent", Input)
        intent = intent_input.value.strip()
        if not intent:
            return
        self.thought_log.write(f"[bold yellow]► Player Intent: {intent}[/bold yellow]\n")
        intent_input.value = ""
        
        if self.ai_process:
            self.thought_log.write("[dim]Intent forwarded to AI...\n[/dim]")
        
        try:
            intent_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "player_intent.txt")
            with open(intent_file, "w") as f:
                f.write(intent)
        except Exception as e:
            self.thought_log.write(f"[red]Failed to save intent: {e}[/red]\n")

    def start_ai(self) -> None:
        if self.ai_process is not None:
            return
            
        import subprocess
        import sys
        import json
        
        self.thought_log.write("[bold green]Starting LLM-Powered AI Agent...[/bold green]\n")
        
        try:
            if not self.app.ai_config.get("api_key"):
                self.thought_log.write("[red]No API key configured. Please set it in AI Config.[/red]\n")
                return
            
            env = os.environ.copy()
            env["AUTH_TOKEN"] = self.app.user_data.get("token", "")
            env["AI_CONFIG"] = json.dumps(self.app.ai_config)
            env["PYTHONUNBUFFERED"] = "1"
            env["CUSTOM_OBJECTIVE"] = self.app.ai_config.get("custom_objective", "")
            
            self.ai_process = subprocess.Popen(
                [sys.executable, "ai_agent.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                preexec_fn=os.setsid
            )
            
            self.query_one("#ai-status", Label).update(" AI Status: [bold green]RUNNING[/bold green]")
            
            import threading
            def read_output():
                for line in iter(self.ai_process.stdout.readline, ""):
                    if line:
                        self.app.call_from_thread(self.post_ai_log, line.strip())
                self.app.call_from_thread(self.on_ai_exit)

            threading.Thread(target=read_output, daemon=True).start()
            
        except Exception as e:
            self.thought_log.write(f"[red]Failed to start AI: {str(e)}[/red]\n")

    def stop_ai(self) -> None:
        if self.ai_process:
            import os
            import signal
            try:
                pgid = os.getpgid(self.ai_process.pid)
                os.killpg(pgid, signal.SIGTERM)
                self.ai_process.wait(timeout=1.0)
            except Exception:
                try:
                    self.ai_process.kill()
                except Exception: pass
            
            self.ai_process = None
            self._ai_objective = ""
            self._ai_progress = ""
            try:
                if self.app is not None and self.is_attached:
                    self.thought_log.write("[bold red]AI Agent and all sub-processes Stopped.[/bold red]\n")
                    self.query_one("#ai-status", Label).update(" AI Status: [bold red]STOPPED[/bold red]")
                    self.query_one("#objectives", ObjectivePanel).update_objectives([{"text": "No active objective", "completed": False, "sub_tasks": []}])
            except Exception:
                pass

    def post_ai_log(self, message: str) -> None:
        if self.app is None or not self.is_attached:
            return
        
        t = TRANSLATIONS[self.app.ai_config.get("language", "Thai")]
        
        if message.startswith("OBJECTIVE:"):
            self._ai_objective = message.replace("OBJECTIVE:", "").strip()
            self._update_ai_objective_display()
        elif message.startswith("PROGRESS:"):
            self._ai_progress = message.replace("PROGRESS:", "").strip()
            self._update_ai_objective_display()
        elif "AGENT: Analyzing" in message:
            self.thought_log.write(f"[cyan]🧠 {t['ai_analyzing']}...[/cyan]\n")
        elif "AGENT: Thinking" in message:
            self.thought_log.write(f"💭 [dim]{t['ai_thinking']}...[/dim]\n")
        elif "AGENT: Processing" in message:
             self.thought_log.write(f"🎯 [bold green]{t['ai_processing']}...[/bold green]\n")
        elif "AGENT: No clear DECISION" in message:
             self.thought_log.write(f"[bold red]❌ {message.replace('AGENT: ', '')}[/bold red]\n")
        elif "AGENT: ---" in message:
             self.thought_log.write(f"[dim]{message}[/dim]\n")
        elif "⚠️ AGENT:" in message:
             self.thought_log.write(f"[yellow]{message}[/yellow]\n")
        elif "❌" in message:
             self.thought_log.write(f"[bold red]{message}[/bold red]\n")
        else:
             self.thought_log.write(f"{message}\n")
    
    def _update_ai_objective_display(self) -> None:
        if not hasattr(self, "_ai_objective") or not self._ai_objective:
            return
        
        try:
            obj_list = []
            obj = {
                "text": self._ai_objective,
                "completed": False,
                "sub_tasks": []
            }
            
            if hasattr(self, "_ai_progress") and self._ai_progress:
                progress = self._ai_progress
                parts = [p.strip() for p in progress.split(",")]
                for part in parts:
                    if "=" in part:
                        key_val = part.split("=")
                        if len(key_val) == 2:
                            resource, progress_val = key_val
                            obj["sub_tasks"].append({
                                "text": f"{resource.strip()} ({progress_val})",
                                "completed": "/" in progress_val and progress_val.split("/")[0] >= progress_val.split("/")[1]
                            })
            
            obj_list.append(obj)
            self.query_one("#objectives", ObjectivePanel).update_objectives(obj_list)
        except Exception:
            pass

    def on_ai_exit(self) -> None:
        self.ai_process = None
        try:
            self.query_one("#ai-status", Label).update(" AI Status: [bold red]STOPPED[/bold red]")
        except Exception: pass

    async def refresh_loop(self) -> None:
        while True:
            self.refresh_data()
            await asyncio.sleep(2)

    def refresh_data(self) -> None:
        try:
            char = self.app.api.get_character_detail()
            if char:
                name = char.get("name", "Anonymous")
                level = char.get("level", 1)
                action = char.get("current_action", "IDLE")
                
                self.app.sub_title = f"👤 {name} | ⭐ Lv.{level} | 🛠️ {action.replace('_', ' ').title()}"
                
                if not hasattr(self, "_last_action") or self._last_action != action:
                    self.action_display.set_action(action)
                    self.game_map.update_player_position(action)
                    self._last_action = action

            resp = self.app.api.get_inventory()
            inv = resp.get("inventory", []) if isinstance(resp, dict) else resp
            inv_items = []
            if inv and isinstance(inv, list):
                for item in inv:
                    item_id = item.get("item_id", "")
                    inv_items.append({
                        "name": item_id,
                        "icon": self.get_icon(item_id),
                        "quantity": item.get("quantity", 0),
                        "level": item.get("level", 0),
                    })
            
            self.query_one("#inventory", InventoryPanel).update_inventory(inv_items)

        except Exception as e:
            pass

    def get_icon(self, name):
        icons = {
            "wooden_axe": "🪓",
            "axe": "🪓",
            "wooden_pickaxe": "⛏️",
            "pickaxe": "⛏️",
            "wooden_sword": "🗡️",
            "sword": "🗡️",
            "wood": "🪵",
            "stone": "🪨",
            "gold": "💰"
        }
        return icons.get(name.lower(), "📦")


class NameChangeScreen(Screen):
    def compose(self) -> ComposeResult:
        with Vertical(id="name-container"):
            yield Label("SET CHARACTER NAME", id="name-title")
            yield Input(placeholder="Enter New Name", id="new-name")
            with Horizontal():
                yield Button("Save", variant="primary", id="btn-save")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            new_name = self.query_one("#new-name", Input).value
            if self.app.api.update_character_name(new_name):
                self.app.pop_screen()
            else:
                self.query_one("#name-title", Label).update("[red]Failed to update name[/red]")
        else:
            self.app.pop_screen()


class CharacterSelectScreen(Screen):
    def __init__(self, characters):
        super().__init__()
        self.characters = characters

    def compose(self) -> ComposeResult:
        with Vertical(id="char-select-container"):
            yield Label("SELECT CHARACTER", id="char-select-title")
            for char in self.characters:
                char_id = char.get("id", "")
                char_name = char.get("name", "Unknown")
                char_level = char.get("level", 1)
                yield Button(f" {char_name} (Lv.{char_level})", id=f"btn-char-{char_id}", variant="primary")
            yield Button("Create New Character", id="btn-create-char", variant="default")
            yield Input(placeholder="New Character Name", id="new-char-name")
            yield Label("", id="char-select-error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id.startswith("btn-char-"):
            char_id = event.button.id.replace("btn-char-", "")
            result = self.app.api.select_character(char_id)
            if result:
                new_token = result.get("token")
                if new_token:
                    self.app.api.set_token(new_token)
                    self.app.user_data["token"] = new_token
                self.app.push_screen(GameScreen())
            else:
                self.query_one("#char-select-error", Label).update("[red]Failed to select character[/red]")
        elif event.button.id == "btn-create-char":
            new_name = self.query_one("#new-char-name", Input).value
            if len(new_name) < 3:
                self.query_one("#char-select-error", Label).update("[red]Name must be at least 3 characters[/red]")
                return
            result = self.app.api.create_character(new_name)
            if result:
                characters = self.app.api.list_characters()
                if characters and characters.get("characters"):
                    chars = characters["characters"]
                    self.app.push_screen(CharacterSelectScreen(chars))
                else:
                    self.app.push_screen(GameScreen())
            else:
                self.query_one("#char-select-error", Label).update("[red]Failed to create character[/red]")


from textual.widgets import Select
from ui_components import ObjectivePanel, InventoryPanel, ActionAnimation, ThoughtLog, GameMapPanel
import asyncio
import os
