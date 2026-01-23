import json
import os
from typing import List, Dict, Any
from .models import User

USERS_FILE = "venv/app/users.json"
RECORDS_FILE = "venv/app/password_records.json"

def load_users() -> List[User]:
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [User(**u) for u in data]
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        print(" users.json повреждён или пуст. Создаём новый.")
        return []

def save_users(users: List[User]):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump([u.model_dump() for u in users], f, ensure_ascii=False, indent=2)

def load_records() -> List[Dict[str, Any]]:
    if not os.path.exists(RECORDS_FILE):
        return []
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_records(records: List[Dict[str, Any]]):
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)