# server/repositories/events_repo.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import pyodbc
from server.config import settings
from server.models.event import (
    Event, EventSearchParams, EventSearchResult,
    AnalyticsSummary, AnalyticsBucket
)

# ---------- DB helper ----------
def _conn():
    # Example:
    # "DRIVER={ODBC Driver 18 for SQL Server};SERVER=eventsdb_hadas.mssql.somee.com;DATABASE=eventsdb_hadas;UID=...;PWD=...;Encrypt=no"
    return pyodbc.connect(settings.DB_URL, autocommit=True)

# ---------- Contract ----------
class EventsRepository(ABC):
    @abstractmethod
    def search(self, params: EventSearchParams) -> EventSearchResult: ...
    @abstractmethod
    def get(self, event_id: str) -> Optional[Event]: ...
    @abstractmethod
    def analytics_summary(self) -> AnalyticsSummary: ...

# ---------- SQL implementation ----------
class SqlEventsRepository(EventsRepository):
    def search(self, params: EventSearchParams) -> EventSearchResult:
        where = []
        args = []

        # free text: Title/Venue/City
        if params.q:
            like = f"%{params.q.strip()}%"
            where.append("(Title LIKE ? OR ISNULL(Venue,'') LIKE ? OR ISNULL(City,'') LIKE ?)")
            args += [like, like, like]

        # exact category
        if params.category:
            where.append("Category = ?")
            args.append(params.category.strip())

        # date range
        if params.from_date:
            where.append("Date >= ?")
            args.append(params.from_date)
        if params.to_date:
            where.append("Date <= ?")
            args.append(params.to_date)

        # the Pydantic model Event requires event_date (not Optional) → exclude NULL dates
        where.append("Date IS NOT NULL")

        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        limit = max(1, params.limit)
        page = max(1, params.page)
        offset = (page - 1) * limit

        with _conn() as conn:
            cur = conn.cursor()

            # total count
            cur.execute(f"SELECT COUNT(*) FROM dbo.Events{where_sql}", args)
            total = cur.fetchone()[0]

            # page query (SQL Server 2012+)
            cur.execute(
                f"""
                SELECT Id, Title, Category, Date,
                       ISNULL(City,''), ISNULL(Venue,''), ISNULL(Country,''), Price
                FROM dbo.Events
                {where_sql}
                ORDER BY Id DESC
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
                """,
                (*args, offset, limit)
            )
            rows = cur.fetchall()

        items: list[Event] = []
        for r in rows:
            # r: (Id, Title, Category, Date, City, Venue, Country, Price)
            city, venue, country = r[4], r[5], r[6]
            location = ", ".join([v for v in [venue, city, country] if v])
            event_date = r[3].date()  # not None, we filtered Date IS NOT NULL

            items.append(Event(
                id=str(r[0]),
                title=r[1],
                category=r[2] or "General",
                event_date=event_date,
                location=location,
                price=float(r[7]) if r[7] is not None else None,
            ))

        pages = (total + limit - 1) // limit
        return EventSearchResult(items=items, total=total, page=page, pages=pages)

    def get(self, event_id: str) -> Optional[Event]:
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT Id, Title, Category, Date,
                       ISNULL(City,''), ISNULL(Venue,''), ISNULL(Country,''), Price
                FROM dbo.Events
                WHERE Id = ? AND Date IS NOT NULL
                """,
                (event_id,)
            )
            r = cur.fetchone()

        if not r:
            return None

        city, venue, country = r[4], r[5], r[6]
        location = ", ".join([v for v in [venue, city, country] if v])
        event_date = r[3].date()  # filtered non-null

        return Event(
            id=str(r[0]),
            title=r[1],
            category=r[2] or "General",
            event_date=event_date,
            location=location,
            price=float(r[7]) if r[7] is not None else None,
        )

    def analytics_summary(self) -> AnalyticsSummary:
        with _conn() as conn:
            cur = conn.cursor()
            # by month (YYYY-MM) from Date, ignoring NULLs
            cur.execute("""
                SELECT CONVERT(char(7), Date, 120) AS ym, COUNT(*)
                FROM dbo.Events
                WHERE Date IS NOT NULL
                GROUP BY CONVERT(char(7), Date, 120)
                ORDER BY ym
            """)
            month_rows = cur.fetchall()

            # by category (NULL → 'General')
            cur.execute("""
                SELECT ISNULL(Category, 'General') AS cat, COUNT(*)
                FROM dbo.Events
                GROUP BY ISNULL(Category, 'General')
                ORDER BY cat
            """)
            cat_rows = cur.fetchall()

        by_month = [AnalyticsBucket(key=r[0], count=r[1]) for r in month_rows]
        by_category = [AnalyticsBucket(key=r[0], count=r[1]) for r in cat_rows]
        return AnalyticsSummary(by_category=by_category, by_month=by_month)

# ---------- Default repo (swap-in for the router) ----------
repo_events: EventsRepository = SqlEventsRepository()
