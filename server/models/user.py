from pydantic import BaseModel, EmailStr
from typing import Literal

class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    hashed_password: str
    role: Literal["USER", "AGENT", "ADMIN"] = "USER"
    agent_status: Literal["NONE", "PENDING", "APPROVED", "REJECTED"] = "NONE"
    is_active: bool = True

class UserPublic(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: Literal["USER", "AGENT", "ADMIN"]
    agent_status: Literal["NONE", "PENDING", "APPROVED", "REJECTED"]
    is_active: bool
