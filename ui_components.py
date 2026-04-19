from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Label, RichLog
from textual.reactive import reactive

from frames import IDLE_FRAMES, WOOD_FRAMES, ROCK_FRAMES, FIGHT_FRAMES


class ObjectivePanel(Static):
    def compose(self) -> ComposeResult:
        yield Label("═══ OBJECTIVES ═══", id="obj-title")
        yield Vertical(id="obj-list")

    def update_objectives(self, objectives):
        container = self.query_one("#obj-list", Vertical)
        container.remove_children()
        
        for obj in objectives:
            status = "[green]✔[/green]" if obj.get("completed") else "[ ]"
            container.mount(Label(f"• {obj.get('text')}", classes="obj-main"))
            for sub in obj.get("sub_tasks", []):
                sub_status = "[green]✔[/green]" if sub.get("completed") else "[ ]"
                container.mount(Label(f"  └─ {sub_status} {sub.get('text')}", classes="obj-sub"))


class InventorySlot(Static):
    item_name = reactive("EMPTY")
    item_icon = reactive("📦")
    quantity = reactive(0)
    level = reactive(0)

    def render(self) -> str:
        if self.item_name == "EMPTY" or not self.item_name:
            return "[dim]    --- EMPTY ---    [/dim]"
        display_name = str(self.item_name).replace('_', ' ').title()
        tools = ["wooden_axe", "wooden_pickaxe", "wooden_sword"]
        if self.item_name in tools and self.level > 0:
            return f"{self.item_icon} [bold]{display_name}[/bold] [yellow]Lv.{self.level}[/yellow] [cyan]x{self.quantity}[/cyan]"
        return f"{self.item_icon} [bold]{display_name}[/bold] [cyan]x{self.quantity}[/cyan]"


class InventoryPanel(Static):
    def compose(self) -> ComposeResult:
        yield Label("═══ INVENTORY ═══", id="inv-title")
        with Horizontal(id="slots-container"):
            yield InventorySlot(id="slot-0")
            yield InventorySlot(id="slot-1")
            yield InventorySlot(id="slot-2")
            yield InventorySlot(id="slot-3")
            yield InventorySlot(id="slot-4")

    def update_inventory(self, items):
        for i in range(5):
            slot = self.query_one(f"#slot-{i}", InventorySlot)
            if i < len(items):
                item = items[i]
                slot.item_name = item.get("name", "Unknown")
                slot.item_icon = item.get("icon", "📦")
                slot.quantity = item.get("quantity", 0)
                slot.level = item.get("level", 0)
                slot.remove_class("empty")
            else:
                slot.item_name = "EMPTY"
                slot.item_icon = "📦"
                slot.quantity = 0
                slot.level = 0
                slot.add_class("empty")


class ActionAnimation(Static):
    current_action = reactive("idle")
    frame_index = reactive(0)
    
    def compose(self) -> ComposeResult:
        yield Label("═══ ACTIONS ═══", id="action-title")
        with Horizontal(id="animation-container"):
            yield Static("", id="action-animation")
        yield Label("", id="action-name")
    
    def on_mount(self):
        self.set_timer(0.1, self._run_frame)
    
    def _run_frame(self):
        if not self.is_mounted:
            return
        
        if self.current_action == "cutting_wood":
            frames = WOOD_FRAMES
            name = "CUTTING WOOD"
            interval = 0.3
        elif self.current_action == "mining_rocks":
            frames = ROCK_FRAMES
            name = "MINING ROCKS"
            interval = 0.25
        elif self.current_action == "fighting_monsters":
            frames = FIGHT_FRAMES
            name = "FIGHTING MONSTERS"
            interval = 0.2
        else:
            frames = IDLE_FRAMES
            name = "IDLE"
            interval = 1.0
        
        frame = frames[self.frame_index % len(frames)]
        self.query_one("#action-animation", Static).update(f"[cyan]{frame}[/cyan]")
        self.query_one("#action-name", Label).update(f"[bold yellow]{name}[/bold yellow]")
        
        self.frame_index += 1
        self.set_timer(interval, self._run_frame)
    
    def set_action(self, action_name: str):
        n = action_name.lower().replace("-", "_").replace(" ", "_")
        if "cut" in n or "wood" in n:
            self.current_action = "cutting_wood"
        elif "mine" in n or "rock" in n or "stone" in n:
            self.current_action = "mining_rocks"
        elif "fight" in n or "monster" in n or "gold" in n:
            self.current_action = "fighting_monsters"
        else:
            self.current_action = "idle"
        self.frame_index = 0


class ActionLog(RichLog):
    def __init__(self, *args, **kwargs):
        kwargs["markup"] = True
        kwargs["wrap"] = True
        super().__init__(*args, **kwargs)


class ThoughtLog(RichLog):
    def __init__(self, *args, **kwargs):
        kwargs["markup"] = True
        kwargs["wrap"] = True
        super().__init__(*args, **kwargs)


class GameMapPanel(Static):
    player_zone = reactive("idle")
    
    def compose(self) -> ComposeResult:
        yield Label("═══ WORLD MAP ═══", id="map-title")
        with Horizontal(id="map-zones"):
            with Vertical(id="zone-forest", classes="map-zone"):
                yield Label("🌲 FOREST", classes="zone-label")
                yield Static("🌲🌲🌲\n🌲🌲🌲\n🌲🌲🌲", id="forest-grid")
            with Vertical(id="zone-mines", classes="map-zone"):
                yield Label("⛏️ MINES", classes="zone-label")
                yield Static("🪨🪨🪨\n🪨🪨🪨\n🪨🪨🪨", id="mines-grid")
            with Vertical(id="zone-battle", classes="map-zone"):
                yield Label("⚔️ BATTLE", classes="zone-label")
                yield Static("👹👹👹\n👹👹👹\n👹👹👹", id="battle-grid")
        yield Label("", id="map-player-pos")
    
    def on_mount(self):
        self.update_player_position("idle")
    
    def update_player_position(self, action: str):
        action = action.lower().replace("-", "_").replace(" ", "_")
        if "cut" in action or "wood" in action:
            zone = "forest"
        elif "mine" in action or "rock" in action or "stone" in action:
            zone = "mines"
        elif "fight" in action or "monster" in action or "gold" in action:
            zone = "battle"
        else:
            zone = "idle"
        
        self.player_zone = zone
        
        for z in ["forest", "mines", "battle"]:
            el = self.query_one(f"#zone-{z}", Vertical)
            if z == zone:
                el.add_class("active-zone")
            else:
                el.remove_class("active-zone")
        
        zone_names = {"forest": "🌲 FOREST", "mines": "⛏️ MINES", "battle": "⚔️ BATTLE", "idle": "🏠 BASE"}
        self.query_one("#map-player-pos", Label).update(f"[bold yellow]► Player at: {zone_names.get(zone, 'UNKNOWN')}[/bold yellow]")
