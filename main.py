import os
import sys
import asyncio
import subprocess
from datetime import datetime
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, Horizontal, Container, Grid
from textual.widgets import Header, Footer, Input, Button, Label, Static, Log, Select
from textual.binding import Binding
from textual.message import Message

from api_client import APIClient
from ui_components import ObjectivePanel, InventoryPanel, ActionLog, ThoughtLog, ActionAnimation, GameMapPanel

TRANSLATIONS = {
    "Thai": {
        "play_ai": "▶ เริ่มบอท AI",
        "stop_ai": "■ หยุดบอท AI",
        "config": "⚙ ตั้งค่า",
        "status_stopped": " สถานะ AI: [bold red]หยุดแล้ว[/bold red]",
        "status_running": " สถานะ AI: [bold green]กำลังทำงาน[/bold green]",
        "objectives": "🎯 เป้าหมาย",
        "inventory": "🎒 กระเป๋า (5 ช่อง)",
        "action_feed": "⚔️ การกระทำ",
        "ai_thoughts": "🧠 ความคิด AI",
        "ai_thinking": "บอทกำลังคิดผ่าน",
        "ai_analyzing": "กำลังวิเคราะห์สถานะเกม",
        "ai_processing": "กำลังดำเนินการตามคำตัดสิน",
        "ai_stopped": "บอท AI และระบบลูกข่ายหยุดทำงานแล้ว",
        "welcome": "ยินดีต้อนรับสู่ DeepIdle!",
        "ai_init": "ระบบ AI เริ่มทำงาน...",
        "active": "สถานะ:",
        "login_title": "กรุณาเข้าสู่ระบบ",
        "username": "ชื่อผู้ใช้",
        "password": "รหัสผ่าน",
        "login": "เข้าสู่ระบบ",
        "signup": "สมัครสมาชิก",
        "config_title": "ตั้งค่า AI ENGINE",
        "engine": "เลือก Engine:",
        "command": "คำสั่ง CLI:",
        "flags": "Flags ที่รัน:",
        "lang": "เลือกภาษา (Language):",
        "save": "บันทึกและปิด",
        "test": "ทดสอบการเชื่อมต่อ"
    },
    "English": {
        "play_ai": "▶ PLAY AI",
        "stop_ai": "■ STOP AI",
        "config": "⚙ CONFIG",
        "status_stopped": " AI Status: [bold red]STOPPED[/bold red]",
        "status_running": " AI Status: [bold green]RUNNING[/bold green]",
        "objectives": "🎯 OBJECTIVES",
        "inventory": "🎒 INVENTORY (5 Slots)",
        "action_feed": "⚔️ ACTIONS",
        "ai_thoughts": "🧠 AI THOUGHTS",
        "ai_thinking": "Thinking via",
        "ai_analyzing": "Analyzing game state",
        "ai_processing": "Processing AI decision",
        "ai_stopped": "AI Agent and all sub-processes Stopped.",
        "welcome": "Welcome to DeepIdle!",
        "ai_init": "AI Logic Initialized...",
        "active": "Active:",
        "login_title": "Please Login or Signup",
        "username": "Username",
        "password": "Password",
        "login": "Login",
        "signup": "Signup",
        "config_title": "AI ENGINE CONFIGURATION",
        "engine": "Select AI Engine:",
        "command": "CLI Command:",
        "flags": "Execution Flags:",
        "lang": "Select Language:",
        "save": "Save & Close",
        "test": "Test Connection"
    }
}

class LoginScreen(Screen):
    """The screen where the user logs in or signs up."""
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
            data = self.app.api.signup(username, password)
            if data:
                error_label.update("[green]Account created! Now login.[/green]")
            else:
                error_label.update("[red]Signup failed[/red]")

PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "default_model": "gpt-4o",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "api_base": "https://api.openai.com/v1"
    },
    "anthropic": {
        "name": "Anthropic",
        "default_model": "claude-3-5-sonnet-20241022",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
        "api_base": "https://api.anthropic.com/v1"
    },
    "google": {
        "name": "Google AI",
        "default_model": "gemini-2.0-flash",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "api_base": "https://generativelanguage.googleapis.com/v1beta"
    },
    "groq": {
        "name": "Groq",
        "default_model": "llama-3.1-70b-versatile",
        "models": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "api_base": "https://api.groq.com/openai/v1"
    },
    "ollama": {
        "name": "Ollama (Local)",
        "default_model": "llama3.1",
        "models": ["llama3.1", "llama3", "mistral", "codellama"],
        "api_base": "http://localhost:11434/v1"
    },
    "minimax": {
        "name": "MiniMax",
        "default_model": "MiniMax-M2.7",
        "models": ["MiniMax-M2.7", "MiniMax-M2.5", "MiniMax-M2.1", "MiniMax-M2.1-lightning", "MiniMax-M2"],
        "api_base": "https://api.minimax.io/v1"
    }
}

class AIConfigScreen(Screen):
    """Screen for configuring LLM settings via litellm."""
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
        # Build options as (label, value) tuples
        options = [(m, m) for m in models]
        model_select.set_options(options)
        # Set value to current if valid, else first model
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
    """The main game interface."""
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
                yield Label(t["ai_thoughts"], classes="pane-title")
                yield ThoughtLog(id="thought-log")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_data() # Initial fetch
        self.refresh_task = asyncio.create_task(self.refresh_loop())
        self.action_display = self.query_one("#action-display", ActionAnimation)
        self.game_map = self.query_one("#game-map", GameMapPanel)
        self.thought_log = self.query_one("#thought-log", ThoughtLog)
        self.ai_process = None
        self._ai_objective = ""
        self._ai_progress = ""
        
        # Initial state
        self.action_display.set_action("idle")
        self.game_map.update_player_position("idle")
        self.thought_log.write("AI Logic Initialized...\n")

    def on_unmount(self) -> None:
        """Cleanup when the screen is removed or app exits."""
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
                # Kill the entire process group (ensures children like 'opencode' are killed)
                pgid = os.getpgid(self.ai_process.pid)
                os.killpg(pgid, signal.SIGTERM)
                
                # Wait briefly for cleanup
                self.ai_process.wait(timeout=1.0)
            except Exception:
                # Force kill the process itself if pgid or wait fails
                try:
                    self.ai_process.kill()
                except Exception: pass
            
            self.ai_process = None
            self._ai_objective = ""
            self._ai_progress = ""
            try:
                # Only write to log/update UI if app is still active
                if self.app is not None and self.is_attached:
                    self.thought_log.write("[bold red]AI Agent and all sub-processes Stopped.[/bold red]\n")
                    self.query_one("#ai-status", Label).update(" AI Status: [bold red]STOPPED[/bold red]")
                    # Clear objectives
                    self.query_one("#objectives", ObjectivePanel).update_objectives([{"text": "No active objective", "completed": False, "sub_tasks": []}])
            except Exception:
                pass

    def post_ai_log(self, message: str) -> None:
        if self.app is None or not self.is_attached:
            return
        
        t = TRANSLATIONS[self.app.ai_config.get("language", "Thai")]
        
        # Parse OBJECTIVE: and PROGRESS: lines from AI
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
        """Update objectives panel with AI's current objective and progress."""
        if not hasattr(self, "_ai_objective") or not self._ai_objective:
            return
        
        try:
            obj_list = []
            obj = {
                "text": self._ai_objective,
                "completed": False,
                "sub_tasks": []
            }
            
            # Parse PROGRESS into sub_tasks if available
            if hasattr(self, "_ai_progress") and self._ai_progress:
                progress = self._ai_progress
                # Format: stone=5/10, wood=10/10, gold=5/10
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
        # Use query_one safely as the screen might have changed
        try:
            self.query_one("#ai-status", Label).update(" AI Status: [bold red]STOPPED[/bold red]")
        except Exception: pass


    async def refresh_loop(self) -> None:
        while True:
            self.refresh_data()
            await asyncio.sleep(2)

    def refresh_data(self) -> None:
        try:
            # Get character status
            char = self.app.api.get_character_detail()
            if char:
                name = char.get("name", "Anonymous")
                level = char.get("level", 1)
                action = char.get("current_action", "IDLE")
                
                self.app.sub_title = f"👤 {name} | ⭐ Lv.{level} | 🛠️ {action.replace('_', ' ').title()}"
                
                # Update Action Animation if action changes
                if not hasattr(self, "_last_action") or self._last_action != action:
                    self.action_display.set_action(action)
                    self.game_map.update_player_position(action)
                    self._last_action = action

            # Get inventory
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
            
            # ALWAYS update, even if empty, to show the empty slots
            self.query_one("#inventory", InventoryPanel).update_inventory(inv_items)

            # Only update objectives if AI has set one (otherwise leave it empty/waiting)
            # AI sets _ai_objective via post_ai_log

        except Exception as e:
            # self.action_log.write(f"[red]Error: {str(e)}[/red]\n")
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

class DeepIdleApp(App):
    """Main Application Class."""
    TITLE = "DEEPIDLE - Terminal GUI"
    CSS = """
    #login-container, #config-container, #name-container {
        align: center middle;
        height: 100%;
        background: $boost;
        padding: 2;
    }
    #config-container {
        width: 60;
        height: auto;
        border: thick $primary;
    }
    #config-title, #login-title, #name-title {
        content-align: center middle;
        width: 100%;
        text-style: bold;
        color: $accent;
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
        background: $boost;
        padding: 0 1;
        align: left middle;
        border-bottom: solid $panel;
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
        border-right: tall $panel;
        layout: vertical;
    }
    ObjectivePanel {
        height: 1fr;
    }
    InventoryPanel {
        height: 18;
        border-top: tall $panel;
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
        border: round $panel;
        padding: 0 1;
        margin: 0 1;
    }
    InventorySlot.empty {
        opacity: 0.5;
    }
    ActionLog, ThoughtLog {
        height: 1fr;
        background: $surface;
        color: $text;
        overflow-x: hidden;
    }
    #action-display {
        height: 20;
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
    }
    #game-map {
        height: 18;
        border-top: solid $panel;
        padding: 1;
    }
    #map-title {
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    #map-zones {
        height: 1fr;
        align: center middle;
    }
    .map-zone {
        width: 20;
        height: 100%;
        align: center middle;
        border: solid $panel;
        margin: 0 1;
        padding: 1;
    }
    .map-zone.active-zone {
        border: solid $accent;
        background: $surface;
    }
    .zone-label {
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }
    #forest-grid, #mines-grid, #battle-grid {
        content-align: center middle;
        text-style: bold;
        width: 100%;
    }
    #map-player-pos {
        content-align: center middle;
        margin-top: 1;
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
        """Reset the screen to apply language changes."""
        self.pop_screen()
        self.push_screen(GameScreen())

    def load_config(self):
        import json
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    return json.load(f)
        except Exception: pass
        return {"provider": "openai", "api_key": "", "model": "gpt-4o", "language": "Thai", "api_base": ""}

    def save_config(self):
        import json
        try:
            with open("config.json", "w") as f:
                json.dump(self.ai_config, f)
        except Exception: pass

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())

    def on_login_success(self, data):
        self.user_data = data
        self.push_screen(GameScreen())

class NameChangeScreen(Screen):
    """Screen for changing character name."""
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

if __name__ == "__main__":
    app = DeepIdleApp()
    app.run()
