from fastapi import HTTPException, status
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64

from app.models import UserCreate, UserLogin, User
from app.database import load_users, save_users

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register_user(user: UserCreate) -> dict:
    users = load_users()

    if any(u.username == user.username for u in users):
        raise HTTPException(status_code=409, detail="Пользователь уже существует")

    hashed_password = pwd_context.hash(user.password)
    fernet_key = Fernet.generate_key()
    encrypted_user_key = base64.urlsafe_b64encode(fernet_key).decode()

    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        encrypted_user_key=encrypted_user_key
    )

    users.append(new_user)
    save_users(users)

    return {"username": new_user.username}

def login_user(credentials: UserLogin) -> dict:
    users = load_users()

    user = next((u for u in users if u.username == credentials.username), None)
    if not user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")

    if not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")

    return {
        "message": "Вход выполнен успешно",
        "username": user.username,
        "user_key": user.encrypted_user_key
    }