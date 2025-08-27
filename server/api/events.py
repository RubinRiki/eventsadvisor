from typing import Optional
from fastapi import APIRouter, Query
from gateway.adapters.ticketmaster import search_events as tm_search

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/search")
async def search_events_route(
    q: Optional[str] = Query(None, description="keyword"),
    city: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    latlong: Optional[str] = Query(None, description="lat,lon e.g. 32.0853,34.7818"),
    radius: Optional[int] = Query(None),
    unit: Optional[str] = Query(None, regex="^(km|miles)$"),
    start: Optional[str] = Query(None, alias="startDateTime", description="UTC ISO8601 e.g. 2025-09-01T00:00:00Z"),
    end: Optional[str] = Query(None, alias="endDateTime"),
    size: int = Query(10, ge=1, le=200),
    page: int = Query(0, ge=0),  # שימי לב: 0-based!
    sort: str = Query("date,asc", description="date,asc|date,desc|name,asc|name,desc|relevance,desc|distance,asc"),
):
    return await tm_search(
        keyword=q, city=city, country=country, latlong=latlong,
        radius=radius, unit=unit, startDateTime=start, endDateTime=end,
        size=size, page=page, sort=sort
    )
