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

RETRO_COLORS = {
    "BACKGROUND": "#0a0a0f",
    "PANEL_BG": "#141420",
    "PRIMARY_TEXT": "#ffd27a",
    "SECONDARY_TEXT": "#87ceeb",
    "ACCENT": "#66ffcc",
    "HEALTH": "#4aff83",
    "DANGER": "#ff5555",
    "MAGIC": "#bd93f9",
    "BORDER": "#5d4d24",
}
