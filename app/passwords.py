# from fastapi import APIRouter, Depends, HTTPException, Request
# from typing import List
# from cryptography.fernet import Fernet, InvalidToken
# import base64
# from datetime import datetime
# from app.models import PasswordRecordCreate, PasswordRecordUpdate, PasswordRecordOut
# from app.database import load_records, save_records
# from app.auth import get_current_username, get_user_key

# router = APIRouter(prefix="/passwords")

# def encrypt(plain: str, key_b64: str) -> str:
#     f = Fernet(base64.urlsafe_b64decode(key_b64))
#     return f.encrypt(plain.encode()).decode()

# def decrypt(enc: str, key_b64: str) -> str:
#     f = Fernet(base64.urlsafe_b64decode(key_b64))
#     try:
#         return f.decrypt(enc.encode()).decode()
#     except InvalidToken:
#         raise HTTPException(500, "Ошибка расшифровки")

# @router.post("/", response_model=PasswordRecordOut, status_code=201)
# def create(
#     record: PasswordRecordCreate,
#     request: Request,
# ):
    
#     username = request.state.username
#     key_b64 = request.state.user_key
#     records = load_records()
#     new_id = max([r["id"] for r in records], default=0) + 1

#     enc_pwd = encrypt(record.password, key_b64)

#     new_rec = {
#         "id": new_id,
#         "username": username,
#         "title": record.title,
#         "login": record.login,
#         "encrypted_password": enc_pwd,
#         "url": record.url,
#         "notes": record.notes,
#         "created_at": datetime.utcnow().isoformat(),
#         "updated_at": datetime.utcnow().isoformat()
#     }

#     records.append(new_rec)
#     save_records(records)

#     return PasswordRecordOut(**{k: v for k, v in new_rec.items() if k != "username"})

# @router.get("/", response_model=List[PasswordRecordOut])
# def list_all(request: Request):
#     username =request.state.username
#     records = load_records()
#     user_recs = [r for r in records if r["username"] == username]
#     return [PasswordRecordOut(**{k: v for k, v in r.items() if k != "username"}) for r in user_recs]

# @router.get("/stats")
# def stats(username: str = Depends(get_current_username)):
#     records = load_records()
#     return {"total": len([r for r in records if r["username"] == username])}

# @router.get("/{record_id}", response_model=PasswordRecordOut)
# def get_one(record_id: int, username: str = Depends(get_current_username)):
#     records = load_records()
#     rec = next((r for r in records if r["id"] == record_id and r["username"] == username), None)
#     if not rec:
#         raise HTTPException(404, "Запись не найдена")
#     return PasswordRecordOut(**{k: v for k, v in rec.items() if k != "username"})

# @router.put("/{record_id}", response_model=PasswordRecordOut)
# def update_full(
#     record_id: int,
#     data: PasswordRecordCreate,
#     username: str = Depends(get_current_username),
#     key_b64: str = Depends(get_user_key)
# ):
#     records = load_records()
#     idx = next((i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username), None)
#     if idx is None:
#         raise HTTPException(404, "Запись не найдена")

#     records[idx].update({
#         "title": data.title,
#         "login": data.login,
#         "encrypted_password": encrypt(data.password, key_b64),
#         "url": data.url,
#         "notes": data.notes,
#         "updated_at": datetime.utcnow().isoformat()
#     })
#     save_records(records)
#     return PasswordRecordOut(**{k: v for k, v in records[idx].items() if k != "username"})

# @router.patch("/{record_id}", response_model=PasswordRecordOut)
# def update_partial(
#     record_id: int,
#     data: PasswordRecordUpdate,
#     username: str = Depends(get_current_username),
#     key_b64: str = Depends(get_user_key)
# ):
#     records = load_records()
#     idx = next((i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username), None)
#     if idx is None:
#         raise HTTPException(404, "Запись не найдена")

#     rec = records[idx]
#     if data.password is not None:
#         rec["encrypted_password"] = encrypt(data.password, key_b64)
#     if data.title is not None: rec["title"] = data.title
#     if data.login is not None: rec["login"] = data.login
#     if data.url is not None: rec["url"] = data.url
#     if data.notes is not None: rec["notes"] = data.notes
#     rec["updated_at"] = datetime.utcnow().isoformat()

#     save_records(records)
#     return PasswordRecordOut(**{k: v for k, v in rec.items() if k != "username"})

# @router.delete("/{record_id}", status_code=204)
# def delete(record_id: int, username: str = Depends(get_current_username)):
#     records = load_records()
#     idx = next((i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username), None)
#     if idx is None:
#         raise HTTPException(404, "Запись не найдена")
#     del records[idx]
#     save_records(records)
#     return None






from fastapi import APIRouter, Request, HTTPException
from typing import List
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime
from base64 import urlsafe_b64decode

from app.models import (
    PasswordRecordCreate,
    PasswordRecordUpdate,
    PasswordRecordOut
)
from app.database import load_records, save_records

router = APIRouter(prefix="/passwords")


def encrypt(plain: str, key_b64: str) -> str:
    key_bytes = urlsafe_b64decode(key_b64)          # ← вот это важно!
    f = Fernet(key_bytes)
    return f.encrypt(plain.encode()).decode()


def decrypt(enc: str, key_b64: str) -> str:
    key_bytes = urlsafe_b64decode(key_b64)
    f = Fernet(key_bytes)
    return f.decrypt(enc.encode()).decode()

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="C:/Users/Игорь/Desktop/pass/venv/app/templates")



@router.get("/add", response_class=HTMLResponse)
async def show_add_form(request: Request):
    return templates.TemplateResponse("add.html", {
        "request": request,
        "error": None
    })

from fastapi import Form
@router.post("/add", response_model=PasswordRecordOut, status_code=201)
async def create_record(
    request: Request,
    title: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    url: str | None = Form(None),
    notes: str | None = Form(None),):
    username = request.state.username
    key_b64 = request.state.user_key

    encrypted_pwd = encrypt(password, key_b64)

    records = load_records()
    new_id = max((r["id"] for r in records), default=0) + 1

    new_record = {
        "id": new_id,
        "username": username,
        "title": title,
        "login": login,
        "encrypted_password": encrypted_pwd,
        "url": url,
        "notes": notes,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    records.append(new_record)
    save_records(records)
    # После успешного сохранения — редирект на список
    return RedirectResponse(url="/passwords", status_code=303)


@router.get("/", response_model=List[PasswordRecordOut])
def get_all_records(request: Request):
    username = request.state.username

    records = load_records()
    user_records = [r for r in records if r["username"] == username]

    return [
        PasswordRecordOut(
            id=r["id"],
            title=r["title"],
            login=r["login"],
            encrypted_password=r["encrypted_password"],
            url=r.get("url"),
            notes=r.get("notes"),
        )
        for r in user_records
    ]



# @router.get("/{record_id}", response_model=PasswordRecordOut)
# def get_one_record(record_id: int, request: Request):
#     username = request.state.username

#     records = load_records()
#     record = next(
#         (r for r in records if r["id"] == record_id and r["username"] == username),
#         None
#     )

#     if not record:
#         raise HTTPException(status_code=404, detail="Запись не найдена")

#     return PasswordRecordOut(
#         id=record["id"],
#         title=record["title"],
#         login=record["login"],
#         encrypted_password=record["encrypted_password"],
#         url=record.get("url"),
#         notes=record.get("notes"),
#     )

# passwords.py


@router.get("/{record_id}", response_class=HTMLResponse)
async def view_record(record_id: int, request: Request):
    username = request.state.username
    key_b64 = request.state.user_key

    records = load_records()
    record = next(
        (r for r in records if r["id"] == record_id and r["username"] == username),
        None
    )

    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена или не принадлежит вам")

    # Расшифровываем пароль только для отображения
    try:
        decrypted_password = decrypt(record["encrypted_password"], key_b64)
    except Exception as e:
        decrypted_password = "[Ошибка расшифровки]"

    return templates.TemplateResponse(
        "view.html",  # создадим новый шаблон
        {
            "request": request,
            "username": username,
            "record": {
                "id": record["id"],
                "title": record["title"],
                "login": record["login"],
                "password": decrypted_password,          # расшифрованный!
                "url": record.get("url", ""),
                "notes": record.get("notes", ""),
                "created_at": record.get("created_at", ""),
                "updated_at": record.get("updated_at", ""),
            }
        }
    )

# passwords.py

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Form
from datetime import datetime
# ... остальные импорты ...

@router.get("/{record_id}/edit", response_class=HTMLResponse)
async def edit_record_form(record_id: int, request: Request):
    username = request.state.username
    key_b64 = request.state.user_key

    records = load_records()
    record = next(
        (r for r in records if r["id"] == record_id and r["username"] == username),
        None
    )

    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    # Расшифровываем пароль для отображения в форме
    try:
        decrypted_password = decrypt(record["encrypted_password"], key_b64)
    except Exception:
        decrypted_password = ""  # или можно показать ошибку, но лучше пустое поле

    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "username": username,
            "record": {
                "id": record["id"],
                "title": record["title"],
                "login": record["login"],
                "password": decrypted_password,
                "url": record.get("url", ""),
                "notes": record.get("notes", ""),
            }
        }
    )


@router.post("/{record_id}/edit")
async def update_record(
    request: Request,
    record_id: int,
    title: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    url: str | None = Form(None),
    notes: str | None = Form(None),
    
):
    username = request.state.username
    key_b64 = request.state.user_key

    records = load_records()
    idx = next(
        (i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username),
        None
    )

    if idx is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    encrypted_pwd = encrypt(password, key_b64)

    records[idx].update({
        "title": title,
        "login": login,
        "encrypted_password": encrypted_pwd,
        "url": url,
        "notes": notes,
        "updated_at": datetime.utcnow().isoformat(),
    })

    save_records(records)

    return RedirectResponse(url="/passwords", status_code=303)

@router.put("/{record_id}", response_model=PasswordRecordOut)
def update_full_record(
    record_id: int,
    data: PasswordRecordCreate,
    request: Request
):
    username = request.state.username
    key_b64   = request.state.user_key

    records = load_records()
    idx = next(
        (i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username),
        None
    )

    if idx is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    encrypted_pwd = encrypt(data.password, key_b64)

    records[idx].update({
        "title": data.title,
        "login": data.login,
        "encrypted_password": encrypted_pwd,
        "url": data.url,
        "notes": data.notes,
        "updated_at": datetime.utcnow().isoformat(),
    })

    save_records(records)

    return PasswordRecordOut(
        id=records[idx]["id"],
        title=records[idx]["title"],
        login=records[idx]["login"],
        encrypted_password=records[idx]["encrypted_password"],
        url=records[idx].get("url"),
        notes=records[idx].get("notes"),
    )


@router.patch("/{record_id}", response_model=PasswordRecordOut)
def update_partial_record(
    record_id: int,
    data: PasswordRecordUpdate,
    request: Request
):
    username = request.state.username
    key_b64   = request.state.user_key

    records = load_records()
    idx = next(
        (i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username),
        None
    )

    if idx is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    rec = records[idx]

    if data.password is not None:
        rec["encrypted_password"] = encrypt(data.password, key_b64)
    if data.title is not None:
        rec["title"] = data.title
    if data.login is not None:
        rec["login"] = data.login
    if data.url is not None:
        rec["url"] = data.url
    if data.notes is not None:
        rec["notes"] = data.notes

    rec["updated_at"] = datetime.utcnow().isoformat()

    save_records(records)

    return PasswordRecordOut(
        id=rec["id"],
        title=rec["title"],
        login=rec["login"],
        encrypted_password=rec["encrypted_password"],
        url=rec.get("url"),
        notes=rec.get("notes"),
    )


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, request: Request):
    username = request.state.username

    records = load_records()
    idx = next(
        (i for i, r in enumerate(records) if r["id"] == record_id and r["username"] == username),
        None
    )

    if idx is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    del records[idx]
    save_records(records)
    return None


# Если хочешь — можно оставить stats как есть, или тоже перевести на request.state
@router.get("/stats")
def get_stats(request: Request):
    username = request.state.username
    records = load_records()
    user_records = [r for r in records if r["username"] == username]
    return {"total": len(user_records)}