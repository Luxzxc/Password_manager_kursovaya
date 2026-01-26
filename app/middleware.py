# app/middleware.py
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, RedirectResponse
from app.database import load_users
from app.auth import get_user_key


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Список путей, которые НЕ требуют авторизации
        public_paths = [
            "/",
            "/login",
            "/register",
            "/static/",
            "/favicon.ico",
        ]

        # Если путь начинается с одного из публичных — пропускаем
        # if any(request.url.path.startswith(p) for p in public_paths):
        #     return await call_next(request)

        # Пытаемся достать username из cookie
        username = request.cookies.get("X-Username")

        if not username:
            # Можно сделать 401 JSON, но для HTML-приложения логичнее редирект
            return RedirectResponse(url="/", status_code=303)

        # Проверяем, существует ли пользователь
        users = load_users()
        user = next((u for u in users if u.username == username), None)

        if not user:
            response = RedirectResponse(url="/", status_code=303)
            response.delete_cookie("X-Username")
            return response

        # Кладём полезные данные в request.state — они будут доступны везде
        request.state.username = username
        request.state.user_key = user.encrypted_user_key   # уже base64

        response = await call_next(request)
        return response