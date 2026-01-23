from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.auth import login_user, register_user, get_current_username, get_user_key
from app.models import UserCreate, UserLogin
from app.passwords import router as passwords_router, load_records

app = FastAPI()
app.mount("/static", StaticFiles(directory="C:/Users/Игорь/Desktop/pass/venv/app/static"), name="static")
templates = Jinja2Templates(directory="C:/Users/Игорь/Desktop/pass/venv/app/templates")

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
        # Сохраняем в cookie (очень упрощённо, для курсовой пойдёт)
        response = RedirectResponse(url="/passwords", status_code=303)
        response.set_cookie(key="X-Username", value=username, httponly=True)
        # В реальном проекте лучше JWT в cookie
        return response
    except HTTPException as e:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": e.detail},
            status_code=e.status_code
        )


@app.get("/passwords", response_class=HTMLResponse)
async def show_passwords(request: Request):
    username = request.cookies.get("X-Username")
    if not username:
        return RedirectResponse(url="/", status_code=303)

    try:
        # Проверяем существование пользователя (можно улучшить)
        _ = get_current_username(username)  # выбросит 401 если нет
    except HTTPException:
        return RedirectResponse(url="/", status_code=303)

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

@app.post("/register", status_code=201)
def api_register(user: UserCreate):
    return register_user(user)


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("X-Username")
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)