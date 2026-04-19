import os
import json
import time
import re
from api_client import APIClient

MAX_MESSAGES = 20


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B\[[0-9;]*m')
    return ansi_escape.sub('', text)


def run_llm(messages, model, api_key, api_base=None, provider=None):
    try:
        import litellm
        litellm.drop_params = True
        
        full_model = model
        if provider == "minimax" and not model.startswith("minimax/"):
            full_model = f"minimax/{model}"
        elif provider == "anthropic" and not model.startswith("anthropic/"):
            full_model = f"anthropic/{model}"
        elif provider == "google" and not model.startswith("gemini/"):
            full_model = f"gemini/{model}"
        
        kwargs = {"model": full_model, "messages": messages, "api_key": api_key}
        if api_base:
            kwargs["api_base"] = api_base
        
        response = litellm.completion(**kwargs)
        return response.choices[0].message.content
        
    except Exception as e:
        return f"ERROR: {str(e)}"


def parse_decision(text):
    match = re.search(r'DECISION:\s*(\w+)(?:\(([^)]*)\))?', text, re.IGNORECASE)
    if not match:
        return None
    
    action = match.group(1).lower()
    value = match.group(2) if match.group(2) else None
    
    if value and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    
    thought = re.sub(r'DECISION:\s*(\w+(?:\([^)]*\))?)', '', text, flags=re.IGNORECASE).strip()
    
    return {"thought": thought, "action": action, "value": value, "item_id": value}


def parse_inventory(inv):
    inv_list = []
    if isinstance(inv, dict) and "inventory" in inv:
        inv_list = inv.get("inventory") or []
    elif isinstance(inv, list):
        inv_list = inv
    
    inv_items = {}
    if isinstance(inv_list, list):
        for item in inv_list:
            if item:
                inv_items[item.get("item_id", "")] = item.get("quantity", 0)
    return inv_list, inv_items


def parse_storage(storage):
    storage_items = {}
    if isinstance(storage, dict) and isinstance(storage.get("storage"), list):
        for item in storage.get("storage", []):
            if item:
                storage_items[item.get("item_id", "")] = item.get("quantity", 0)
    return storage_items


def fetch_game_state(client):
    status = client.get_character_detail()
    inv = client.get_inventory()
    upgrade_opts = client.get_upgrade_options()
    
    if not status or not inv:
        return None
    
    inv_list, inv_items = parse_inventory(inv)
    storage = client.get_global_storage()
    storage_items = parse_storage(storage)
    
    char_id = status.get("id", "")
    
    return {
        "character": {
            "id": char_id,
            "name": status.get("name"),
            "level": status.get("level"),
            "action": status.get("current_action")
        },
        "inventory": inv_list,
        "inventory_summary": inv_items,
        "global_storage": storage_items,
        "upgrade_requirements": upgrade_opts if isinstance(upgrade_opts, dict) else {}
    }


def execute_action(client, decision):
    action_type = decision.get("action")
    thought = decision.get("thought", "Thinking...")
    print(f"🧠 AI Thought: {thought}", flush=True)
    
    if action_type in ("set_action", "set_character_action"):
        val = decision.get("value")
        print(f"🎯 Action: Setting action to {val}", flush=True)
        client.set_action(val)
    
    elif action_type in ("upgrade", "upgrade_item"):
        item = decision.get("item_id")
        print(f"🎯 Action: Upgrading {item}", flush=True)
        client.upgrade_item(item)
    
    elif action_type in ("claim", "claim_resources"):
        inv = client.get_inventory()
        inv_count = 0
        if isinstance(inv, dict) and "inventory" in inv:
            inv_count = len(inv.get("inventory", []))
        elif isinstance(inv, list):
            inv_count = len(inv)
        
        if inv_count >= 5:
            print(f"⚠️ Cannot claim - inventory is full ({inv_count}/5)! Must deposit first.", flush=True)
        else:
            print("🎯 Action: Claiming resources", flush=True)
            client.claim_resources()
    
    elif action_type in ("deposit", "deposit_to_storage"):
        parts = decision.get("value", "").split(",")
        if len(parts) >= 2:
            item_id = parts[0].strip()
            quantity = int(parts[1].strip())
            print(f"🎯 Action: Depositing {quantity} {item_id} to storage", flush=True)
            client.deposit_to_storage(item_id, quantity)
        else:
            print(f"❓ Invalid deposit format: {decision.get('value')}", flush=True)
    
    elif action_type in ("withdraw", "withdraw_from_storage"):
        parts = decision.get("value", "").split(",")
        if len(parts) >= 2:
            item_id = parts[0].strip()
            quantity = int(parts[1].strip())
            print(f"🎯 Action: Withdrawing {quantity} {item_id} from storage", flush=True)
            client.withdraw_from_storage(item_id, quantity)
        else:
            print(f"❓ Invalid withdraw format: {decision.get('value')}", flush=True)
    
    elif action_type in ("check_upgrade_requirements", "continue", "continue_current_action"):
        print(f"ℹ️ INFO: {action_type} - no action needed, current action continues", flush=True)
    
    else:
        print(f"❓ Unknown action: {action_type}", flush=True)


def build_system_prompt(lang):
    try:
        with open("howtoplay.md", "r") as f:
            instructions = f.read()
    except Exception:
        instructions = "You are an AI playing DeepIdle. Your goal is to upgrade items by gathering resources and spending them wisely."
    
    return f"""### INSTRUCTIONS
{instructions}

### LANGUAGE
You MUST respond and think in {lang}.

### AVAILABLE TOOLS (use when DECIDING to take action)
- set_character_action(action): ตั้ง action (cutting_wood, mining_rocks, fighting_monsters)
- claim_resources: รับ resources สะสม
- upgrade_item(item_id): อัพเกรด item
- deposit_to_storage(item_id, quantity): ฝากเข้า global storage
- withdraw_from_storage(item_id, quantity): ถอนจาก global storage

### ACTION REQUIREMENTS (must have tool in inventory!)
- cutting_wood: ต้องมี wooden_axe ใน inventory
- mining_rocks: ต้องมี wooden_pickaxe ใน inventory
- fighting_monsters: ต้องมี wooden_sword ใน inventory

### INFO (already available in game state, NOT tools to call)
- get_character_status: เช็ค level, name, current_action
- get_inventory: เช็ค inventory (ดูว่ามี tools อะไรบ้าง)
- check_upgrade_requirements: ดูสูตร upgrade (ดูได้เลยไม่ต้องเรียก)
- get_global_storage: ดู global storage (ดูได้เลยไม่ต้องเรียก)

### CRITICAL: INVENTORY FULL = CANNOT CLAIM!
- Inventory มีแค่ 5 slots!
- เริ่มต้น: wooden_axe, wooden_pickaxe, wooden_sword (3 slots)
- ถ้าเก็บ resources ครบ 5 ชนิด = เต็ม = claim_resources จะล้มเหลว!
- เต็มแล้วต้อง: deposit ไป global storage ก่อน แล้วค่อย withdraw กลับมา

### IMPORTANT: YOU CAN DEPOSIT TOOLS TOO!
- deposit_to_storage ใช้ได้กับทุก item_id รวมถึง tools (wooden_axe, wooden_pickaxe, wooden_sword)
- ถ้าเก็บ tools เข้า global storage จะเก็บ level ไว้ด้วย
- ถ้าต้องการพื้นที่ว่างใน inventory สามารถ deposit tools ที่ไม่ได้ใช้ชั่วคราวได้

### EXAMPLE: INVENTORY FULL SCENARIO
inventory = [
  {{"item_id": "wooden_axe", "level": 3}},
  {{"item_id": "wooden_pickaxe", "level": 2}},
  {{"item_id": "wooden_sword", "level": 1}},
  {{"item_id": "wood", "quantity": 50}},
  {{"item_id": "stone", "quantity": 30}}     ← slot 5 = เต็ม!
]
ถ้าจะเก็บ gold ต้อง: deposit_to_storage(wood, 50) ก่อน!

### UPGRADE FORMULA
- wooden_axe: wood=N*5, gold=N*10
- wooden_pickaxe: stone=N*5, wood=N*5, gold=N*10  
- wooden_sword: wood=N*5, gold=N*10

### OUTPUT FORMAT
Always output your current objective and progress, then end with DECISION:

OBJECTIVE: [your current goal in 1 sentence]
PROGRESS: [resources collected so far] / [resources needed]
DECISION: tool_name
or
DECISION: tool_name(argument)

NOTE: Do NOT use "continue" as an action. The current action continues automatically until you change it.

Examples:
OBJECTIVE: Upgrade wooden_pickaxe to Lv.2
PROGRESS: stone=5/10, wood=10/10, gold=5/10
DECISION: set_character_action(mining_rocks)

OBJECTIVE: Upgrade wooden_axe to Lv.3
PROGRESS: wood=10/15, gold=5/15
DECISION: upgrade_item(wooden_axe)

OBJECTIVE: Inventory full - need to deposit
PROGRESS: slots=5/5
DECISION: deposit_to_storage(wood, 20)

# Tool deposit example (if you want to free a slot)
OBJECTIVE: Need slot for new resource
PROGRESS: slots=5/5
DECISION: deposit_to_storage(wooden_sword, 1)

# IMPORTANT: If you want to fight monsters but don't have wooden_sword
# You must: withdraw_from_storage(wooden_sword, 1) first!
# Or if it's in global storage from another player
"""


def main():
    token = os.environ.get("AUTH_TOKEN")
    config_json = os.environ.get("AI_CONFIG", "{}")
    
    try:
        ai_config = json.loads(config_json)
    except:
        ai_config = {}
    
    provider = ai_config.get("provider", "openai")
    api_key = ai_config.get("api_key", "")
    model = ai_config.get("model", "gpt-4o")
    api_base = ai_config.get("api_base", "")
    lang = ai_config.get("language", "Thai")
    
    if not token or not api_key:
        print("ERROR: No auth token or API key configured")
        return
    
    print("🚀 AI Agent (litellm) started...", flush=True)
    
    api_url = os.environ.get("GAME_API_URL", "http://localhost:3000/api")
    client = APIClient(base_url=api_url, source="AI-Agent")
    client.set_token(token)
    
    system_prompt = build_system_prompt(lang)
    messages = [{"role": "system", "content": system_prompt}]
    
    while True:
        try:
            print("AGENT: Analyzing game state...", flush=True)
            state = fetch_game_state(client)
            
            if not state:
                print("ERROR: Failed to fetch state. Retrying...", flush=True)
                time.sleep(5)
                continue
            
            user_prompt = f"""### CURRENT GAME STATE
{json.dumps(state, indent=2)}

### TASK
Based on the state, decide your next move. End with DECISION: action_type
"""
            
            messages.append({"role": "user", "content": user_prompt})
            print("AGENT: Thinking via LLM...", flush=True)
            
            raw_output = run_llm(messages, model, api_key, api_base if api_base else None, provider)
            clean_output = strip_ansi(raw_output)
            messages.append({"role": "assistant", "content": clean_output})
            
            if len(messages) > MAX_MESSAGES:
                messages = [messages[0]] + messages[-(MAX_MESSAGES-1):]
            
            print("AGENT: Processing AI decision...", flush=True)
            decision = parse_decision(clean_output)
            
            if decision:
                execute_action(client, decision)
            else:
                print(f"⚠️ No DECISION found in LLM response", flush=True)
                print(f"RAW: {clean_output}", flush=True)
            
            time.sleep(10)
            
        except Exception as e:
            print(f"ERROR: {str(e)}", flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()