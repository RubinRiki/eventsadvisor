from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Iterable
from datetime import date
from uuid import uuid4
from collections import Counter, defaultdict
from server.models.event import Event, EventSearchParams, EventSearchResult, AnalyticsSummary, AnalyticsBucket

class EventsRepository(ABC):
    @abstractmethod
    def search(self, params: EventSearchParams) -> EventSearchResult: ...
    @abstractmethod
    def get(self, event_id: str) -> Optional[Event]: ...
    @abstractmethod
    def analytics_summary(self) -> AnalyticsSummary: ...

class InMemoryEventsRepository(EventsRepository):
    def __init__(self) -> None:
        self._items: list[Event] = _seed_events()

    def _filter(self, params: EventSearchParams) -> Iterable[Event]:
        items = self._items
        if params.q:
            q = params.q.lower()
            items = [e for e in items if q in e.title.lower() or q in e.location.lower()]
        if params.category:
            items = [e for e in items if e.category.lower() == params.category.lower()]
        if params.from_date:
            items = [e for e in items if e.event_date >= params.from_date]
        if params.to_date:
            items = [e for e in items if e.event_date <= params.to_date]
        return items

    def search(self, params: EventSearchParams) -> EventSearchResult:
        items = list(self._filter(params))
        total = len(items)
        limit = max(1, params.limit)
        page = max(1, params.page)
        start = (page - 1) * limit
        end = start + limit
        page_items = items[start:end]
        pages = (total + limit - 1) // limit
        return EventSearchResult(items=page_items, total=total, page=page, pages=pages)

    def get(self, event_id: str) -> Optional[Event]:
        for e in self._items:
            if e.id == event_id:
                return e
        return None

    def analytics_summary(self) -> AnalyticsSummary:
        by_category = Counter(e.category for e in self._items)
        by_month = defaultdict(int)
        for e in self._items:
            key = e.event_date.strftime("%Y-%m")
            by_month[key] += 1
        return AnalyticsSummary(
            by_category=[AnalyticsBucket(key=k, count=v) for k, v in sorted(by_category.items())],
            by_month=[AnalyticsBucket(key=k, count=v) for k, v in sorted(by_month.items())],
        )

def _seed_events() -> list[Event]:
    base = [
        ("Tech Summit", "Conference", "Tel Aviv", date(2025, 9, 10), 399.0),
        ("AI Meetup", "Meetup", "Haifa", date(2025, 9, 18), None),
        ("Music Fest", "Festival", "Jerusalem", date(2025, 10, 3), 180.0),
        ("Art Expo", "Exhibition", "Tel Aviv", date(2025, 11, 12), 75.0),
        ("Startup Night", "Meetup", "Beer Sheva", date(2025, 9, 25), None),
        ("Data Conf", "Conference", "Herzliya", date(2025, 12, 2), 520.0),
    ]
    out: list[Event] = []
    for title, category, location, d, price in base:
        out.append(Event(id=str(uuid4()), title=title, category=category, location=location, event_date=d, price=price))
    return out

# default repo instance for now; later swap to DB-backed impl
repo_events = InMemoryEventsRepository()
