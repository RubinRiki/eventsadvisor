# event.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal
from datetime import datetime

class Event(BaseModel):
    id: str
    title: str
    category: str       
    location: str
    starts_at: datetime
    ends_at: Optional[datetime] = None
    status: Literal["DRAFT","PUBLISHED","CANCELLED"] = "PUBLISHED"
    capacity: int = Field(ge=0, default=0)
    image_url: Optional[HttpUrl] = None
    created_by: str
    price: Optional[float] = None  

class EventSearchParams(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: int = 1
    limit: int = 10
