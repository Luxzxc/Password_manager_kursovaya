from fastapi import APIRouter, Depends, HTTPException
from typing import List
from cryptography.fernet import Fernet, InvalidToken
import base64
from datetime import datetime
from app.models import PasswordRecordCreate, PasswordRecordUpdate, PasswordRecordOut
from app.database import load_records, save_records
from app.auth import get_current_username, get_user_key

router = APIRouter(prefix="/passwords")

def encrypt(plain: str, key_b64: str) -> str:
    f = Fernet(base64.urlsafe_b64decode(key_b64))
    return f.encrypt(plain.encode()).decode()

def decrypt(enc: str, key_b64: str) -> str:
    f = Fernet(base64.urlsafe_b64decode(key_b64))
    try:
        return f.decrypt(enc.encode()).decode()
    except InvalidToken:
        raise HTTPException(500, "Ошибка расшифровки")

@router.post("/", response_model=PasswordRecordOut, status_code=201)
def create(
    record: PasswordRecordCreate,
    username: str = Depends(get_current_username),
    key_b64: str = Depends(get_user_key)
):
    records = load_records()
    new_id = max([r["id"] for r in records], default=0) + 1

    enc_pwd = encrypt(record.password, key_b64)

    new_rec = {
        "id": new_id,
        "username": username,
        "title": record.title,
        "login": record.login,
        "encrypted_password": enc_pwd,
        "url": record.url,
        "notes": record.notes,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    records.append(new_rec)
    save_records(records)

    return PasswordRecordOut(**{k: v for k, v in new_rec.items() if k != "username"})

@router.get("/", response_model=List[PasswordRecordOut])
def list_all(username: str = Depends(get_current_username)):
    records = load_records()
    user_recs = [r for r in records if r["username"] == username]
    return [PasswordRecordOut(**{k: v for k, v in r.items() if k != "username"}) for r in user_recs]

@router.get("/stats")
def stats(username: str = Depends(get_current_username)):
    records = load_records()
    return {"total": len([r for r in records if r["username"] == username])}

@router.get("/{record_id}", response_model=PasswordRecordOut)
def get_one(record_id: int, username: str = Depends(get_current_username)):
    records = load_records()
    rec = next((r for r in records if r["id"] == record_id and r["username"] == username), None)
    if not rec:
        raise HTTPException(404, "Запись не найдена")
    return PasswordRecordOut(**{k: v for k, v in rec.items() if k != "username"})

@router.put("/{record_id}", response_model=PasswordRecordOut)
def update_full(
    record_id: int,
    data: PasswordRecordCreate,
    username: str = Depends(get_current_username),
    key_b64: str = Depends(get_user_key)
):
    records = load_records()
    idx = next((i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username), None)
    if idx is None:
        raise HTTPException(404, "Запись не найдена")

    records[idx].update({
        "title": data.title,
        "login": data.login,
        "encrypted_password": encrypt(data.password, key_b64),
        "url": data.url,
        "notes": data.notes,
        "updated_at": datetime.utcnow().isoformat()
    })
    save_records(records)
    return PasswordRecordOut(**{k: v for k, v in records[idx].items() if k != "username"})

@router.patch("/{record_id}", response_model=PasswordRecordOut)
def update_partial(
    record_id: int,
    data: PasswordRecordUpdate,
    username: str = Depends(get_current_username),
    key_b64: str = Depends(get_user_key)
):
    records = load_records()
    idx = next((i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username), None)
    if idx is None:
        raise HTTPException(404, "Запись не найдена")

    rec = records[idx]
    if data.password is not None:
        rec["encrypted_password"] = encrypt(data.password, key_b64)
    if data.title is not None: rec["title"] = data.title
    if data.login is not None: rec["login"] = data.login
    if data.url is not None: rec["url"] = data.url
    if data.notes is not None: rec["notes"] = data.notes
    rec["updated_at"] = datetime.utcnow().isoformat()

    save_records(records)
    return PasswordRecordOut(**{k: v for k, v in rec.items() if k != "username"})

@router.delete("/{record_id}", status_code=204)
def delete(record_id: int, username: str = Depends(get_current_username)):
    records = load_records()
    idx = next((i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username), None)
    if idx is None:
        raise HTTPException(404, "Запись не найдена")
    del records[idx]
    save_records(records)
    return None

