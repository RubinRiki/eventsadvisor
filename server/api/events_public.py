from typing import Optional
from datetime import date
from fastapi import APIRouter, Query, HTTPException, Depends 
from server.core.deps import get_current_user                
from server.models.user import User
from server.models.event import Event, EventSearchResult, EventSearchParams, AnalyticsSummary
from server.repositories.events_repo import repo_events

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/search", response_model=EventSearchResult)
def search_events(
    q: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    params = EventSearchParams(q=q, category=category, from_date=from_date, to_date=to_date, page=page, limit=limit)
    return repo_events.search(params)

@router.get("/{event_id}", response_model=Event)
def get_event(event_id: str):
    ev = repo_events.get(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="event not found")
    return ev

@router.get("/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary(current: User = Depends(get_current_user)):
    return repo_events.analytics_summary()
