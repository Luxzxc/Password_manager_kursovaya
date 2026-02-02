from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, RedirectResponse
from app.database import load_users
from app.auth import get_user_key


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        path = request.url.path

        # Публичные маршруты — пропускаем без проверки
        if path in {"/", "/login", "/register", "/logout"} or \
           path.startswith("/static/") or \
           path.startswith("/docs") or \
           path.startswith("/openapi.json") or \
           path == "/favicon.ico":
            return await call_next(request)

        # Дальше — только авторизованные запросы
        username = request.cookies.get("X-Username")
        if not username:
            return RedirectResponse(url="/", status_code=303)

        users = load_users()
        user = next((u for u in users if u.username == username), None)
        if not user:
            response = RedirectResponse(url="/", status_code=303)
            response.delete_cookie("X-Username")
            return response

        request.state.username = username
        request.state.user_key = user.encrypted_user_key

        return await call_next(request)