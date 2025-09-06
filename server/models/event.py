# server/models/event.py
from __future__ import annotations
from typing import Optional, List, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field

# Event statuses aligned with API/DB
EventStatus = Literal["DRAFT", "PUBLISHED", "ARCHIVED"]

# ---------- Base / Create / Update / Public ----------

class EventBase(BaseModel):
    title: str
    category: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    capacity: int = Field(default=0, ge=0)
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    status: EventStatus = "DRAFT"

class EventCreate(EventBase):
    title: str = Field(min_length=1)

class EventUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    capacity: Optional[int] = Field(default=None, ge=0)
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    status: Optional[EventStatus] = None

class EventPublic(EventBase):
    id: int
    owner_id: Optional[int] = None
    created_at: Optional[datetime] = None

# ---------- Search params / results ----------

class EventSearchParams(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    page: int = 1
    limit: int = 10

class EventSearchResult(BaseModel):
    total: int
    page: int
    limit: int
    items: List[EventPublic]

# ---------- Lightweight analytics summary used by /events/analytics/summary ----------
class EventAnalyticsSummary(BaseModel):   
    total_events: int
    total_registrations_confirmed: int
    total_waitlist: int
    total_likes: int
    total_saves: int
