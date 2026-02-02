from fastapi import FastAPI, Request, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.auth import login_user, register_user, get_current_username, get_user_key
import app.models
from app.models import UserCreate, UserLogin
from app.passwords import router as passwords_router, load_records
from app.database import load_users
from datetime import datetime
from app.passwords import encrypt, get_all_records
from app.database import save_records
from app.middleware import AuthMiddleware

app = FastAPI()
app.add_middleware(AuthMiddleware)
app.mount("/static", StaticFiles(directory="venv/app/static"), name="static")
templates = Jinja2Templates(directory="venv/app/templates")

app.include_router(passwords_router)


@app.get("/", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
async def process_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    try:
        result = login_user(UserLogin(username=username, password=password))
        response = RedirectResponse(url="/passwords", status_code=303)
        response.set_cookie(key="X-Username", value=username, httponly=True)
        return response
    except HTTPException as e:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": e.detail},
            status_code=e.status_code
        )


@app.get("/passwords", response_class=HTMLResponse)
async def show_passwords(request: Request):
    username = request.state.username

    records = load_records()
    user_records = [r for r in records if r["username"] == username]

    return templates.TemplateResponse(
        "passwords.html",
        {
            "request": request,
            "username": username,
            "records": user_records
        }
    )


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("X-Username")
    return response

@app.get("/register", response_class=HTMLResponse)
def show_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@app.post("/register", response_class=HTMLResponse)
def process_register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    try:
        register_user(UserCreate(username=username, password=password))
        # сразу логиним после успешной регистрации
        response = RedirectResponse(url="/passwords", status_code=303)
        response.set_cookie(key="X-Username", value=username, httponly=True, max_age=86400)
        return response
    except HTTPException as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": e.detail
        }, status_code=e.status_code)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)