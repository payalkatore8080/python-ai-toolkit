import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HISTORY_FILE = PROJECT_ROOT / "web_chat_history.json"


def load_history(user_id=None):
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)

        if user_id is None:
            return history

        return [
            chat for chat in history
            if chat.get("owner_id") == user_id
        ]

    except (json.JSONDecodeError, OSError):
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def claim_unowned_chats(user_id):
    history = load_history()
    changed = False

    for chat in history:
        if "owner_id" not in chat:
            chat["owner_id"] = user_id
            changed = True

    if changed:
        save_history(history)


def create_chat(user_id):
    history = load_history()

    chat = {
        "id": str(uuid4()),
        "owner_id": user_id,
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now().isoformat()
    }

    history.append(chat)
    save_history(history)
    return chat


def add_message(chat_id, role, content, user_id):
    history = load_history()

    for chat in history:
        if chat["id"] == chat_id and chat.get("owner_id") == user_id:
            chat["messages"].append({
                "role": role,
                "content": content
            })

            if chat["title"] == "New Chat" and role == "user":
                chat["title"] = content[:40]

            save_history(history)
            return True

    return False


def delete_chat(chat_id, user_id):
    history = load_history()

    updated_history = [
        chat for chat in history
        if not (
            chat["id"] == chat_id
            and chat.get("owner_id") == user_id
        )
    ]

    save_history(updated_history)
    return len(updated_history) != len(history)


def clear_chat(chat_id, user_id):
    history = load_history()

    for chat in history:
        if chat["id"] == chat_id and chat.get("owner_id") == user_id:
            chat["messages"] = []
            chat["title"] = "New Chat"
            save_history(history)
            return True

    return False
