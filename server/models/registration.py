from __future__ import annotations
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field

RegistrationStatus = Literal["CONFIRMED", "WAITLIST", "CANCELLED"]

class RegistrationCreate(BaseModel):
    event_id: int
    quantity: int = Field(1, gt=0)

class RegistrationPublic(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: RegistrationStatus
    created_at: datetime

class Registration(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: RegistrationStatus
    quantity: int = 1
    total_price: float | None = None
    created_at: datetime
