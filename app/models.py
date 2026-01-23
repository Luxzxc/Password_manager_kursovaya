from pydantic import BaseModel, Field
from typing import Optional
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class User(BaseModel):
    username: str
    hashed_password: str
    encrypted_user_key: str

# Модели для записей паролей
class PasswordRecordCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    login: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)
    url: Optional[str] = None
    notes: Optional[str] = None

class PasswordRecordUpdate(BaseModel):
    title: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None

class PasswordRecordOut(BaseModel):
    id: int
    title: str
    login: str
    encrypted_password: str
    url: Optional[str] = None
    notes: Optional[str] = None