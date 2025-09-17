from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.core.deps import get_db, get_current_user, require_any
from server.models.user import UserPublic as User
from server.models.event import (
    EventPublic, EventCreate, EventUpdate,
    EventSearchParams, EventSearchResult,
    EventStatus, EventAnalyticsSummary
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
    db: Session = Depends(get_db),
):
    params = EventSearchParams(q=q, category=category, from_date=from_date, to_date=to_date, page=page, limit=limit)
    return repo_events.search(db, params)

@router.get("/{event_id}", response_model=EventPublic)
def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = repo_events.get(db, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="event not found")
    return EventPublic.model_validate(ev.model_dump())

@router.post("", response_model=EventPublic, status_code=status.HTTP_201_CREATED)
def create_event(
    body: EventCreate,
    current: User = Depends(require_any("AGENT", "ADMIN")),
    db: Session = Depends(get_db),
):
    ev = repo_events.create(db, owner_id=int(current.id), data=body)
    return EventPublic.model_validate(ev.model_dump())

@router.patch("/{event_id}", response_model=EventPublic)
def update_event(
    event_id: int,
    body: EventUpdate,
    current: User = Depends(require_any("AGENT", "ADMIN")),
    db: Session = Depends(get_db),
):
    exists = repo_events.get(db, event_id)
    if not exists:
        raise HTTPException(status_code=404, detail="event not found")
    ev2 = repo_events.update(db, event_id=event_id, data=body, requester=current)
    return EventPublic.model_validate(ev2.model_dump())

@router.post("/{event_id}/publish", response_model=EventPublic)
def publish_event(
    event_id: int,
    current: User = Depends(require_any("AGENT", "ADMIN")),
    db: Session = Depends(get_db),
):
    exists = repo_events.get(db, event_id)
    if not exists:
        raise HTTPException(status_code=404, detail="event not found")
    ev2 = repo_events.set_status(db, event_id, EventStatus.PUBLISHED, requester=current)
    return EventPublic.model_validate(ev2.model_dump())

@router.post("/{event_id}/archive", response_model=EventPublic)
def archive_event(
    event_id: int,
    current: User = Depends(require_any("AGENT", "ADMIN")),
    db: Session = Depends(get_db),
):
    exists = repo_events.get(db, event_id)
    if not exists:
        raise HTTPException(status_code=404, detail="event not found")
    ev2 = repo_events.set_status(db, event_id, EventStatus.ARCHIVED, requester=current)
    return EventPublic.model_validate(ev2.model_dump())

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    current: User = Depends(require_any("AGENT", "ADMIN")),
    db: Session = Depends(get_db),
):
    exists = repo_events.get(db, event_id)
    if not exists:
        raise HTTPException(status_code=404, detail="event not found")
    repo_events.delete(db, event_id, requester=current)
    return

@router.get("/mine/list", response_model=List[EventPublic])
def list_my_events(
    current: User = Depends(require_any("AGENT", "ADMIN")),
    db: Session = Depends(get_db),
):
    items = repo_events.list_for_owner(db, owner_id=int(current.id), requester=current)
    return [EventPublic.model_validate(e.model_dump()) for e in items]

@router.get("/analytics/summary", response_model=EventAnalyticsSummary)
def analytics_summary(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return repo_events.analytics_summary(db)
