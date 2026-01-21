from app.database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.secure import create_access_token, verify_password, oauth2_scheme, get_password_hash, get_current_user
from datetime import timedelta
from typing import Annotated
from app.config import settings
from app.models import User
from app.schemas import UserCreate, UserOut, Token
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI(
    title="Защищённый Менеджер Паролей",
    description="Курсовая работа по дисциплине Основы программирования",
    version="0.0.1"
)

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World! Сервер работает :)"}

@app.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    # Генерация Fernet-ключа (добавьте шифрование по ТЗ)
    from cryptography.fernet import Fernet
    user_key = Fernet.generate_key()
    encrypted_user_key = user_key.decode()  # Храните зашифрованным по ТЗ
    new_user = User(username=user.username, hashed_password=hashed_password, encrypted_user_key=encrypted_user_key)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # Для stateless JWT просто верните OK; для invalidation используйте blacklist (не в ТЗ)
    return {"message": "Logged out"}

@app.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)