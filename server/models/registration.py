from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class RegistrationCreate(BaseModel):
    event_id: str
    quantity: int = Field(1, gt=0)  # אופציונלי

class Registration(BaseModel):
    id: str
    user_id: str
    event_id: str
    status: Literal["CONFIRMED","WAITLIST","CANCELLED"]
    quantity: int = 1
    total_price: float | None = None
    created_at: datetime
