from __future__ import annotations
from typing import Optional, List, Tuple
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from server.models.db_models import EventDB
from server.models.event import (
    EventPublic, EventCreate, EventUpdate,
    EventSearchParams, EventSearchResult, EventStatus
)
from server.models.user import User

class EventsRepo:
    def _to_public(self, e: EventDB) -> EventPublic:
        return EventPublic(
            id=e.Id,
            title=e.Title,
            category=e.Category,
            venue=e.Venue,
            city=e.City,
            country=e.Country,
            price=float(e.Price) if e.Price is not None else None,
            description=e.description,
            image_url=e.image_url,
            capacity=e.capacity,
            starts_at=e.starts_at,
            ends_at=e.ends_at,
            status=e.status,
            owner_id=getattr(e, "OwnerId", None) if hasattr(e, "OwnerId") else None,
            created_at=e.CreatedAt,
        )

    def get(self, db: Session, event_id: int) -> Optional[EventPublic]:
        obj = db.get(EventDB, event_id)
        return self._to_public(obj) if obj else None

    def search(self, db: Session, params: EventSearchParams) -> EventSearchResult:
        q = db.query(EventDB)
        if params.q:
            like = f"%{params.q}%"
            q = q.filter(or_(EventDB.Title.ilike(like),
                             EventDB.Category.ilike(like),
                             EventDB.City.ilike(like)))
        if params.category:
            q = q.filter(EventDB.Category == params.category)
        if params.from_date:
            q = q.filter(EventDB.starts_at >= datetime(params.from_date.year, params.from_date.month, params.from_date.day))
        if params.to_date:
            q = q.filter(EventDB.starts_at <= datetime(params.to_date.year, params.to_date.month, params.to_date.day, 23, 59, 59))

        total = q.count()
        items = (q.order_by(EventDB.starts_at.asc().nullslast())
                   .offset((params.page - 1) * params.limit)
                   .limit(params.limit)
                   .all())
        return EventSearchResult(
            total=total,
            page=params.page,
            limit=params.limit,
            items=[self._to_public(e) for e in items],
        )

    def create(self, db: Session, owner_id: int, data: EventCreate) -> EventPublic:
        obj = EventDB(
            Title=data.title,
            Category=data.category,
            Venue=data.venue,
            City=data.city,
            Country=data.country,
            Price=data.price,
            description=data.description,
            image_url=data.image_url,
            capacity=data.capacity or 0,
            starts_at=data.starts_at,
            ends_at=data.ends_at,
            status=data.status or EventStatus.DRAFT,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return self._to_public(obj)

    def update(self, db: Session, event_id: int, data: EventUpdate, requester: User) -> EventPublic:
        obj = db.get(EventDB, event_id)
        if not obj:
            raise ValueError("event not found")

        # Optional ownership check if you store owner_id on EventDB
        # if requester.role == "AGENT" and getattr(obj, "OwnerId", requester.id) != requester.id:
        #     raise PermissionError("forbidden")

        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "title": obj.Title = value
            elif field == "category": obj.Category = value
            elif field == "venue": obj.Venue = value
            elif field == "city": obj.City = value
            elif field == "country": obj.Country = value
            elif field == "price": obj.Price = value
            elif field == "description": obj.description = value
            elif field == "image_url": obj.image_url = value
            elif field == "capacity": obj.capacity = value
            elif field == "starts_at": obj.starts_at = value
            elif field == "ends_at": obj.ends_at = value
            elif field == "status": obj.status = value

        db.commit()
        db.refresh(obj)
        return self._to_public(obj)

    def set_status(self, db: Session, event_id: int, status: str, requester: User) -> EventPublic:
        obj = db.get(EventDB, event_id)
        if not obj:
            raise ValueError("event not found")
        obj.status = status
        db.commit()
        db.refresh(obj)
        return self._to_public(obj)

    def delete(self, db: Session, event_id: int, requester: User) -> None:
        obj = db.get(EventDB, event_id)
        if not obj:
            return
        db.delete(obj)
        db.commit()

    def list_for_owner(self, db: Session, owner_id: int, requester: User) -> List[EventPublic]:
        # If there is no OwnerId column, return all for ADMIN and just a placeholder for AGENT
        q = db.query(EventDB)
        # If you add OwnerId later:
        # if requester.role == "AGENT":
        #     q = q.filter(EventDB.OwnerId == owner_id)
        items = q.order_by(EventDB.CreatedAt.desc()).all()
        return [self._to_public(e) for e in items]

    def analytics_summary(self, db: Session):
        # Use DB views created earlier:
        row = db.execute("SELECT * FROM v_analytics_totals").fetchone()
        return {
            "total_users": row.total_users if row else 0,
            "total_events": row.total_events if row else 0,
            "total_registrations_confirmed": row.total_registrations_confirmed if row else 0,
            "total_waitlist": row.total_waitlist if row else 0,
            "total_likes": row.total_likes if row else 0,
            "total_saves": row.total_saves if row else 0,
        }

repo_events = EventsRepo()
