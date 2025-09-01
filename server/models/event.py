from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class Event(BaseModel):
    id: str
    title: str
    category: str
    location: str
    event_date: date
    price: Optional[float] = Field(default=None)

class EventSearchParams(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    page: int = 1
    limit: int = 10

class EventSearchResult(BaseModel):
    items: list[Event]
    total: int
    page: int
    pages: int

class AnalyticsBucket(BaseModel):
    key: str
    count: int

class AnalyticsSummary(BaseModel):
    by_category: list[AnalyticsBucket]
    by_month: list[AnalyticsBucket]
