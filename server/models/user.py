from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

Role = Literal["USER", "AGENT", "ADMIN"]
AgentStatus = Literal["NONE", "REQUESTED", "APPROVED", "REJECTED"]

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Role = "USER"
    agent_status: AgentStatus = "NONE"
    is_active: bool = True
    password_hash: Optional[str] = None

class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Role
    agent_status: AgentStatus = "NONE"
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
