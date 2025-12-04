import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def _user_path(user_id: str):
    user_dir = os.path.join(DATA_DIR, "users", user_id or "default")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, "vocab_book.json")

def load(user_id: str = "default"):
    book_path = _user_path(user_id)
    if not os.path.exists(book_path):
        return []
    try:
        with open(book_path, "r", encoding="utf-8") as f:
            return json.load(f) or []
    except Exception:
        return []

def save(items, user_id: str = "default"):
    book_path = _user_path(user_id)
    with open(book_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def list_items(user_id: str = "default"):
    return load(user_id)

def add_item(term: str, explanation: str, example: str, target_language: str, user_id: str = "default"):
    items = load(user_id)
    for it in items:
        if it.get("term") == term and it.get("target_language") == target_language:
            return False
    items.append({
        "term": term,
        "explanation": explanation,
        "example": example,
        "target_language": target_language,
        "added_at": datetime.utcnow().isoformat()
    })
    save(items, user_id)
    return True

def remove_item(term: str, target_language: str = None, user_id: str = "default"):
    items = load(user_id)
    new_items = []
    for it in items:
        if it.get("term") == term and (target_language is None or it.get("target_language") == target_language):
            continue
        new_items.append(it)
    save(new_items, user_id)
    return len(new_items) != len(items)
