# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Server — models/user.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
Pydantic schemas for user flows:
- Create/Login payloads from client
- Public user shape returned by the API (never exposes password_hash)
- Internal "in DB" shape if needed by services
- Token/Response models for auth endpoints

Notes:
- Uses Pydantic v2 config (`from_attributes=True`) to allow ORM objects.
- API fields are snake_case; DB can keep PascalCase — mapping is handled by services.
"""

from __future__ import annotations
from typing import Optional, Literal
from datetime import datetime

from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict  # Pydantic v2

# ---------- Enums ----------
Role = Literal["USER", "AGENT", "ADMIN"]
AgentStatus = Literal["NONE", "REQUESTED", "APPROVED", "REJECTED"]


# ---------- Base with common config ----------
class _BaseModel(BaseModel):
    # Allow constructing from ORM objects (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)


# ---------- Incoming payloads ----------
class UserCreate(_BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(_BaseModel):
    email: EmailStr
    password: str


class UserUpdate(_BaseModel):
    username: Optional[str] = None
    role: Optional[Role] = None
    agent_status: Optional[AgentStatus] = None
    is_active: Optional[bool] = None


# ---------- Public shapes (API responses) ----------
class UserPublic(_BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Role = "USER"
    agent_status: AgentStatus = "NONE"
    is_active: bool = True
    created_at: Optional[datetime] = None  # present if service maps it


# Optional: detailed user (if ever needed in admin screens)
class UserDetailed(UserPublic):
    # Add admin-only fields in the future (e.g., last_login) — no password_hash here.
    pass


# ---------- Internal shape (never return this to clients) ----------
class UserInDB(_BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Role = "USER"
    agent_status: AgentStatus = "NONE"
    is_active: bool = True
    password_hash: str
    created_at: Optional[datetime] = None


# ---------- Auth tokens ----------
class Token(_BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(_BaseModel):
    token: Token
    user: UserPublic
