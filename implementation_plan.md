# Implementation Plan - Terminal GUI Client (DeepIdle)

สร้าง Client สำหรับรันใน Terminal ที่มีความสวยงาม (Premium TUI) โดยใช้ภาษา Python ร่วมกับ Library `Textual` เพื่อความรวดเร็วในการพัฒนาและรองรับ Layout ที่ซับซ้อน

## User Review Required

> [!IMPORTANT]
> **การรับข้อมูล AI Logs:** ในเบื้องต้น Client จะรองรับการแสดงผล Log โดยคาดหวังแหล่งข้อมูล (เช่น File หรือ API endpoint) ที่เก็บ "ความคิดของ AI" เพื่อนำมา Render ทางด้านขวา หากคุณมีวิธีการเชื่อมต่อ AI Log ที่เฉพาะเจาะจง โปรดแจ้งให้ทราบ

## Proposed Changes

### [NEW] Client Directory `client/`

สร้างโปรเจกต์ Python Client แยกออกมาจาก Server

#### [NEW] [requirements.txt](file:///Users/macbook-phachpatkamon/deepidle/client/requirements.txt)
- `textual`: สำหรับสร้าง Terminal GUI
- `requests`: สำหรับเชื่อมต่อ Game Server API
- `python-dotenv`: สำหรับจัดการ Environment (ถ้ามี)

#### [NEW] [main.py](file:///Users/macbook-phachpatkamon/deepidle/client/main.py)
- ไฟล์หลักสำหรับรัน Application
- จัดการ Screen Switching (Login -> Game)
- จัดการ State ของตัวละครและ Inventory

#### [NEW] [api_client.py](file:///Users/macbook-phachpatkamon/deepidle/client/api_client.py)
- Wrapper สำหรับเรียกใช้ API ของ Go Server (`/api/auth`, `/api/character`, `/api/inventory`)

#### [NEW] [ui_components.py](file:///Users/macbook-phachpatkamon/deepidle/client/ui_components.py)
- นิยาม Widgets ต่างๆ:
    - `InventoryPanel`: แสดง 5 ช่องเก็บของพร้อม Emoji
    - `ObjectivePanel`: แสดง Tree เป้าหมาย
    - `ActionLog`: แสดงผลการกระทำ (Log กลาง)
    - `ThoughtLog`: แสดงความคิด AI (Panel ขวา)

---

### UI Design Mockup (Terminal)

```
+-----------------------------------------------------------+
| [DeepIdle v1.0]                                           |
+-------------------------------+---------------------------+
| [Objective Tree]              | [AI Mental State / Logs]  |
| 🎯 Upgrade Axe -> Woodcut     | > Thinking: I need wood   |
| ├─ [ ] Collect Wood (0/10)    | > Planning: Moving to...  |
| └─ [ ] Upgrade at Level 2     | > Logic: If axe < 2 then..|
+-------------------------------+                           |
| [Action Results]              |                           |
| 🪵 You cut wood (+1)          |                           |
| 🪵 You cut wood (+1)          |                           |
+-------------------------------+                           |
| [Inventory (5 Slots)]         |                           |
| [🪓 Axe] [⛏️ Pick] [🗡️ Sword] |                           |
| [🪵 Wood: 2] [EMPTY]          |                           |
+-------------------------------+---------------------------+
| CTR+Q: Quit | CTR+N: Name     | CTR+L: Logout             |
+-----------------------------------------------------------+
```

## Open Questions

1. **การยืนยันการตั้งชื่อตัวละคร:** ใน API ปัทจจุบัน `/api/auth/signup` จะใช้ username/password เลย ต้องการให้มีขั้นตอน "ตั้งชื่อตัวละคร" แยกต่างหากหลังจาก Login ครั้งแรกหรือไม่? (อ้างอิง: เพิ่มระบบ Patch Name ให้แล้ว)
2. **AI Logs Source:** ข้อมูล AI Thoughts จะส่งผ่านช่องทางใด? (ปัจจุบัน Mock ให้ดูเป็นตัวอย่าง)

## Verification Plan

### Automated Tests
- ทดสอบ Login/Signup ผ่าน UI เทียบกับข้อมูลใน MongoDB
- ทดสอบ Inventory Update เมื่อมีการเรียก `ClaimResources` API

### Manual Verification
- รัน `python main.py` ใน Terminal ขนาดมาตรฐาน (80x24) และขนาดใหญ่ เพื่อเช็ก Responsive Layout
- ทดสอบจำลอง (Mock) ข้อมูล AI Log เพื่อดูความไหลลื่นของการเลื่อน (Scrolling)
