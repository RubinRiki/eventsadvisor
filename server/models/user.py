from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    role: str = "user"
    is_active: bool = True

class UserPublic(BaseModel):
    id: str
    email: EmailStr
    role: str
    is_active: bool

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
