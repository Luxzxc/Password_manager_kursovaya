from app.database import Base, engine, get_db
from fastapi import Depends, FastAPI
import uvicorn
from app.models import User, PasswordRecord
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.secure import create_access_token, verify_password, oauth2_scheme, get_password_hash, get_current_user
from datetime import timedelta
from typing import Annotated
from app.config import settings
app = FastAPI(
    title="Защищённый Менеджер Паролей",
    description="Курсовая работа по дисциплине Основы программирования",
    version="0.0.1"
)

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World! Сервер работает :)"}

@app.get("/test-db")
def test_db(db=Depends(get_db)):
    users_count = db.query(User).count()
    return {"status": "БД работает", "users_in_db": users_count}


fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": get_password_hash("testpass123"),  # в реальности из БД
    }
}

@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Временная проверка (потом из БД)
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
@app.get("/users/me")
async def read_users_me(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user




if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)