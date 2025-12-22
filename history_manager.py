import json
import uuid
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("chat_history.json")

def load_history():
    if not HISTORY_FILE.exists():
        return []
    return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))

def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")

def new_chat():
    history = load_history()
    chat = {
        "id": str(uuid.uuid4()),
        "title": "New Chat",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mode": "General Web",
        "messages": [],
        "papers": []
    }
    history.insert(0, chat)
    save_history(history)
    return chat["id"]
