from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RegistrationCreate(BaseModel):
    event_id: str
    notes: Optional[str] = None

class Registration(BaseModel):
    id: str
    user_id: str
    event_id: str
    notes: Optional[str] = None
    created_at: datetime
