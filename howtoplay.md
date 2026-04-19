# How to Play DeepIdle as an AI Agent

## 🏗️ Project Architecture
- **Game Server (Go)**: Backend managing characters, inventory, actions (`localhost:3000`)
- **MCP Server (Node.js)**: Tools for AI to interact with Game Server
- **TUI Client (Python)**: GUI display and AI orchestrator

## 🎯 Goal
Upgrade items by gathering resources efficiently.

## 🔧 Available Tools (MCP)

| Tool | Description |
|------|-------------|
| `login_system(username, password)` | Login to game server |
| `get_character_status` | Check level, name, current_action |
| `get_inventory` | Check your 5-slot inventory |
| `check_upgrade_requirements` | Get upgrade costs for all items |
| `set_character_action(action)` | Set gathering action |
| `claim_resources` | Collect gathered resources |
| `upgrade_item(item_id)` | Spend resources to upgrade item |
| `get_global_storage` | Check community storage |
| `deposit_to_storage(item_id, quantity)` | Deposit to global storage |
| `withdraw_from_storage(item_id, quantity)` | Withdraw from global storage |

## 📦 Inventory System
- **5 slots total** (starts with 3 tools: wooden_axe, wooden_pickaxe, wooden_sword = 3 slots used)
- Each slot = 1 item type (can stack)
- **If full (5 types), cannot claim resources!**
- Must deposit items to global storage to free slots

## ⛏️ Resource Gathering
| Action | Produces | Tool Used |
|--------|----------|-----------|
| `cutting_wood` | wood | wooden_axe |
| `mining_rocks` | stone | wooden_pickaxe |
| `fighting_monsters` | gold | wooden_sword |

## 📈 Upgrade Formula
| Item | Cost |
|------|------|
| wooden_axe Lv.N → N+1 | wood = N×5, gold = N×10 |
| wooden_pickaxe Lv.N → N+1 | stone = N×5, wood = N×5, gold = N×10 |
| wooden_sword Lv.N → N+1 | wood = N×5, gold = N×10 |

## 🔄 Optimal Loop
1. `get_inventory` + `check_upgrade_requirements`
2. If resources sufficient → `upgrade_item`
3. If inventory full → `deposit_to_storage` to free slots
4. If missing resources → `set_character_action` + wait + `claim_resources`
5. Repeat

## 💡 Tips
- Global storage is shared with ALL players - deposit excess, withdraw when needed
- Focus on upgrading one tool at a time
- wooden_pickaxe needs 3 resources (stone, wood, gold) - hardest to upgrade
