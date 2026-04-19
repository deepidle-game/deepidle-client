# DeepIdle Client

Terminal GUI client for the DeepIdle AI-driven idle game.

## Overview

A Python-based TUI (Terminal User Interface) that provides:
- Login/signup to game server
- Real-time game state visualization (inventory, actions, map)
- AI agent orchestration with multi-provider LLM support
- Thai and English language support

## Prerequisites

- Python 3.10+
- Go server running on localhost:3000
- API key for LLM provider (OpenAI, Anthropic, Google, Groq, Ollama, or MiniMax)

## Installation

```bash
cd client

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

On first run, configure your LLM provider:
1. Click the **⚙ CONFIG** button
2. Select your AI provider (OpenAI, Anthropic, Google, Groq, Ollama, MiniMax)
3. Enter your API key
4. Select model and language
5. Click **Save**

Your config is stored in `config.json`.

## Running

```bash
python main.py
```

### Controls
- **ctr+q** - Quit
- **ctr+n** - Change character name
- **ctr+s** - AI configuration

### AI Agent
- Click **▶ PLAY AI** to start the AI agent
- Click **■ STOP AI** to stop the AI agent
- The AI reads `howtoplay.md` for game instructions

## Project Structure

```
client/
├── main.py           # TUI app entry point
├── ai_agent.py       # LLM-powered game automation
├── api_client.py     # HTTP client for game server
├── ui_components.py  # Textual widgets
├── config.json       # LLM provider settings (generated)
├── howtoplay.md      # AI agent instructions
├── requirements.txt  # Python dependencies
└── venv/            # Virtual environment (do not commit)
```

## Dependencies

- `textual` - TUI framework
- `requests` - HTTP client
- `litellm` - Unified LLM interface

## Troubleshooting

**Connection refused**: Ensure the Go server is running on localhost:3000

**AI not starting**: Check that you have a valid API key in config

**Inventory full**: The AI will automatically deposit items to global storage when inventory (5 slots) is full