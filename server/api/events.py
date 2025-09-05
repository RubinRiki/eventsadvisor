from typing import Optional, List
from datetime import date, datetime
from fastapi import APIRouter, Query, HTTPException, Depends, status
from server.core.deps import get_current_user, require_any
from server.models.user import User
from server.models.event import (
    EventPublic, EventCreate, EventUpdate,
    EventSearchParams, EventSearchResult,
    EventStatus, AnalyticsSummary
)
from server.repositories.events_repo import repo_events

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/search", response_model=EventSearchResult)
def search_events(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    params = EventSearchParams(q=q, category=category, from_date=from_date, to_date=to_date, page=page, limit=limit)
    return repo_events.search(params)

@router.get("/{event_id}", response_model=EventPublic)
def get_event(event_id: int):
    ev = repo_events.get(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="event not found")
    return EventPublic.model_validate(ev.model_dump())

@router.post("", response_model=EventPublic, status_code=status.HTTP_201_CREATED)
def create_event(body: EventCreate, current: User = Depends(require_any("AGENT", "ADMIN"))):
    ev = repo_events.create(owner_id=int(current.id), data=body)
    return EventPublic.model_validate(ev.model_dump())

@router.patch("/{event_id}", response_model=EventPublic)
def update_event(event_id: int, body: EventUpdate, current: User = Depends(require_any("AGENT", "ADMIN"))):
    ev = repo_events.get(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="event not found")
    ev2 = repo_events.update(event_id=event_id, data=body, requester=current)
    return EventPublic.model_validate(ev2.model_dump())

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, current: User = Depends(require_any("AGENT", "ADMIN"))):
    ev = repo_events.get(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="event not found")
    repo_events.delete(event_id=event_id, requester=current)
    return

@router.get("/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary(_: User = Depends(get_current_user)):
    return repo_events.analytics_summary()
