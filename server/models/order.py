# server/models/order.py
from pydantic import BaseModel, conint
from datetime import datetime

from pydantic import BaseModel, Field, conint
from datetime import datetime

class RegistrationCreate(BaseModel):
    event_id: int
    quantity: int = Field(..., gt=0)  # כמות חייבת להיות > 0

class Registration(BaseModel):
    id: int
    user_id: int
    event_id: int
    quantity: int
    total_price: float
    created_at: datetime
