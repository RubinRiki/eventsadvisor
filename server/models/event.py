# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Server — models/event.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
Pydantic schemas for Event entities:
- Create/Update payloads from client
- Public shape returned by the API
- Search params & paginated results
- Lightweight analytics summary

DB ↔ API field mapping:
- DB has PascalCase columns (Id, Title, Category, City, CreatedAt, CreatedBy, Url ...)
- API exposes snake_case (id, title, category, city, created_at, owner_id, url ...)
- We use Pydantic v2 with `from_attributes=True` and explicit `alias` on fields,
  so ORM objects (SQLAlchemy) can be dumped directly without manual dict mapping.
"""

from __future__ import annotations

from typing import Optional, List, Literal
from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator


# ---------------- Enums ----------------
EventStatus = Literal["DRAFT", "PUBLISHED", "ARCHIVED"]


# ---------------- Base (shared) ----------------
class _BaseModel(BaseModel):
    # allow constructing from ORM objects and map aliased fields
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class EventBase(_BaseModel):
    # API field      ← DB column (via alias)
    title: str = Field(..., alias="Title")
    category: Optional[str] = Field(default=None, alias="Category")
    venue: Optional[str] = Field(default=None, alias="Venue")
    city: Optional[str] = Field(default=None, alias="City")
    country: Optional[str] = Field(default=None, alias="Country")
    price: Optional[float] = Field(default=None, alias="Price")
    description: Optional[str] = Field(default=None, alias="description")  # Text in DB
    image_url: Optional[str] = Field(default=None, alias="image_url")
    url: Optional[str] = Field(default=None, alias="Url")
    capacity: int = Field(default=0, ge=0, alias="capacity")
    starts_at: Optional[datetime] = Field(default=None, alias="starts_at")
    ends_at: Optional[datetime] = Field(default=None, alias="ends_at")
    status: EventStatus = Field(default="DRAFT", alias="status")

    @model_validator(mode="after")
    def _validate_dates(self):
        # if both dates exist, ensure logical order
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValueError("ends_at must be greater than or equal to starts_at")
        return self


# ---------------- Create / Update ----------------
class EventCreate(EventBase):
    title: str = Field(min_length=1, alias="Title")


class EventUpdate(_BaseModel):
    # all fields optional for PATCH semantics
    title: Optional[str] = Field(default=None, alias="Title")
    category: Optional[str] = Field(default=None, alias="Category")
    venue: Optional[str] = Field(default=None, alias="Venue")
    city: Optional[str] = Field(default=None, alias="City")
    country: Optional[str] = Field(default=None, alias="Country")
    price: Optional[float] = Field(default=None, alias="Price")
    description: Optional[str] = Field(default=None, alias="description")
    image_url: Optional[str] = Field(default=None, alias="image_url")
    url: Optional[str] = Field(default=None, alias="Url")
    capacity: Optional[int] = Field(default=None, ge=0, alias="capacity")
    starts_at: Optional[datetime] = Field(default=None, alias="starts_at")
    ends_at: Optional[datetime] = Field(default=None, alias="ends_at")
    status: Optional[EventStatus] = Field(default=None, alias="status")

    @model_validator(mode="after")
    def _validate_dates(self):
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValueError("ends_at must be greater than or equal to starts_at")
        return self


# ---------------- Public (API response) ----------------
class EventPublic(EventBase):
    id: int = Field(alias="Id")
    owner_id: Optional[int] = Field(default=None, alias="CreatedBy")
    created_at: Optional[datetime] = Field(default=None, alias="CreatedAt")


# ---------------- Search ----------------
class EventSearchParams(_BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    page: int = 1
    limit: int = 10


class EventSearchResult(_BaseModel):
    total: int
    page: int
    limit: int
    items: List[EventPublic]


# ---------------- Analytics (lightweight) ----------------
class EventAnalyticsSummary(_BaseModel):
    total_events: int
    total_registrations_confirmed: int
    total_waitlist: int
    total_likes: int
    total_saves: int
