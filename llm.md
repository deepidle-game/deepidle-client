# DeepIdle Client - LLM Context

## Overview
Python TUI client for DeepIdle game. Provides terminal GUI and AI agent orchestration.

## Architecture
```
User (TUI) ←→ Python App ←→ Go Server API (localhost:3000)
                    ↓
            AI Agent (litellm)
```

## Key Files

### main.py
- Entry point using Textual TUI framework
- Screens: LoginScreen, AIConfigScreen, GameScreen, NameChangeScreen
- Manages app state and screen transitions
- Binds AI agent process via subprocess

### ai_agent.py
- LLM-powered game automation agent
- Uses litellm for multi-provider LLM calls (OpenAI, Anthropic, Google, Groq, Ollama, MiniMax)
- Parses DECISION: action(value) from LLM responses
- Available actions: set_character_action, claim_resources, upgrade_item, deposit_to_storage, withdraw_from_storage

### api_client.py
- APIClient class wraps all HTTP calls to Go server
- Methods: login, signup, get_character_detail, set_action, claim_resources, get_inventory, get_upgrade_options, upgrade_item, update_character_name, get_global_storage, deposit_to_storage, withdraw_from_storage
- Base URL: http://localhost:3000/api

### ui_components.py
- Textual widgets: ObjectivePanel, InventoryPanel, ActionLog, ThoughtLog, ActionAnimation, GameMapPanel

### config.json
- Stores AI provider config (provider, api_key, model, language, api_base)
- **CONTAINS CREDENTIALS - DO NOT COMMIT**

### howtoplay.md
- Game rules and optimal loop for AI agent
- Upgrade formulas and inventory system

## Game State Structure
```json
{
  "character": { "name": "", "level": 1, "current_action": "IDLE" },
  "inventory": [{ "item_id": "wooden_axe", "level": 1, "quantity": 0 }, ...],
  "global_storage": { "item_id": "wood", "quantity": 100 }
}
```

## API Endpoints Used
- POST /api/auth/signin
- POST /api/auth/signup
- GET /api/character/detail
- POST /api/character/action
- POST /api/character/claim
- GET /api/inventory
- GET /api/inventory/upgrade-options
- POST /api/inventory/upgrade
- PATCH /api/character/name
- GET /api/storage
- POST /api/storage/deposit
- POST /api/storage/withdraw

## LLM Integration
- Provider selection (OpenAI/Anthropic/Google/Groq/Ollama/MiniMax)
- Model configuration per provider
- System prompt built from howtoplay.md + dynamic game state
- Conversation history maintained (last 20 messages)
- ANSI color codes stripped from LLM responses

## Credentials
- API keys stored in config.json
- Auth token passed via AUTH_TOKEN environment variable
- AI config passed via AI_CONFIG environment variable (JSON)