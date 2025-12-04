import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
BOOK_PATH = os.path.join(DATA_DIR, "vocab_book.json")

def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def load():
    _ensure_data_dir()
    if not os.path.exists(BOOK_PATH):
        return []
    try:
        with open(BOOK_PATH, "r", encoding="utf-8") as f:
            return json.load(f) or []
    except Exception:
        return []

def save(items):
    _ensure_data_dir()
    with open(BOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def list_items():
    return load()

def add_item(term: str, explanation: str, example: str, target_language: str):
    items = load()
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
    save(items)
    return True

def remove_item(term: str, target_language: str = None):
    items = load()
    new_items = []
    for it in items:
        if it.get("term") == term and (target_language is None or it.get("target_language") == target_language):
            continue
        new_items.append(it)
    save(new_items)
    return len(new_items) != len(items)

