# server/api/events.py
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  # ← הוסף שורה זו
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from decimal import Decimal
from datetime import datetime

from server.infra.db import get_db
from server.models.db_models import EventDB

router = APIRouter(prefix="/events", tags=["events"])

def _to_iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if isinstance(dt, datetime) else None

def _to_float(x):
    return float(x) if isinstance(x, Decimal) else (x if x is None else float(x))

# ... למעלה בלי שינוי ...

@router.get("/search")
def search_events(
    q: str | None = Query(None, description="free text: title/city/venue"),
    category: str | None = None,
    page: int = 1,
    limit: int = 12,
    db: Session = Depends(get_db),
):
    page = max(page, 1)
    limit = max(min(limit, 100), 1)

    # 1) בונים WHERE בנפרד בלי ORDER BY
    base = select(EventDB)
    if q:
        like = f"%{q}%"
        base = base.where(
            or_(
                EventDB.Title.ilike(like),
                EventDB.City.ilike(like),
                EventDB.Venue.ilike(like),
            )
        )
    if category:
        base = base.where(EventDB.Category == category)

    # 2) COUNT ללא ORDER BY (חשוב!)
    total = db.execute(
        select(func.count()).select_from(base.subquery())
    ).scalar_one()

    # 3) מיון רק לשאילתת הדף
    stmt = base.order_by(EventDB.CreatedAt.desc(), EventDB.Id.desc())

    offset = (page - 1) * limit
    rows = db.execute(stmt.offset(offset).limit(limit)).scalars().all()

    items = []
    for e in rows:
        items.append({
            "id": getattr(e, "Id", None) or getattr(e, "id", None),
            "title": getattr(e, "Title", None),
            "city": getattr(e, "City", None),
            "venue": getattr(e, "Venue", None),
            "starts_at": _to_iso(getattr(e, "starts_at", None)), 
            "price": _to_float(getattr(e, "Price", None)),
            "image_url": getattr(e, "image_url", None),
        })

    payload = {"total": total, "page": page, "limit": limit, "items": items}
    return JSONResponse(content=jsonable_encoder(payload))  # ← זה העיקר

@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    e = db.get(EventDB, event_id)
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")

    data = {
        "id": getattr(e, "Id", None) or getattr(e, "id", None),
        "title": getattr(e, "Title", None),
        "category": getattr(e, "Category", None),
        "venue": getattr(e, "Venue", None),
        "city": getattr(e, "City", None),
        "country": getattr(e, "Country", None),
        "url": getattr(e, "Url", None),
        "created_at": _to_iso(getattr(e, "CreatedAt", None)),
        "price": _to_float(getattr(e, "Price", None)),
        "starts_at": _to_iso(getattr(e, "starts_at", None)),
        "ends_at": _to_iso(getattr(e, "ends_at", None)),
        "status": getattr(e, "status", None),
        "capacity": getattr(e, "capacity", None),
        "description": getattr(e, "description", None),
        "image_url": getattr(e, "image_url", None),
        "created_by": getattr(e, "CreatedBy", None),
    }
    return JSONResponse(content=jsonable_encoder(data))
