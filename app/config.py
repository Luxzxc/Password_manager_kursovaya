# app/config.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file = ".env",          # ← файл в корне проекта
        env_file_encoding = "utf-8",
        extra = "ignore"                       # игнорировать лишние переменные
    )


settings = Settings()