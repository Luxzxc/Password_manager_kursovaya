import json
import os
from app.models import User

DATA_FILE = "users.json"

def load_users() -> list[User]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [User(**item) for item in data]
    except:
        return []

def save_users(users: list[User]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([u.model_dump() for u in users], f, ensure_ascii=False, indent=2)