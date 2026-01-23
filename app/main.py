from fastapi import FastAPI
import uvicorn

from app.auth import register_user, login_user
from app.models import UserCreate, UserLogin

app = FastAPI(title="Password Manager (JSON)")

@app.post("/register", status_code=201)
def register(user: UserCreate):
    return register_user(user)

@app.post("/login")
def login(credentials: UserLogin):
    return login_user(credentials)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)