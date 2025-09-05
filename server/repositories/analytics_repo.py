from __future__ import annotations
from sqlalchemy.orm import Session

class AnalyticsRepo:
    def totals(self, db: Session):
        row = db.execute("SELECT * FROM v_analytics_totals").fetchone()
        return {
            "total_users": row.total_users if row else 0,
            "total_events": row.total_events if row else 0,
            "total_registrations_confirmed": row.total_registrations_confirmed if row else 0,
            "total_waitlist": row.total_waitlist if row else 0,
            "total_likes": row.total_likes if row else 0,
            "total_saves": row.total_saves if row else 0,
        }

    def by_month(self, db: Session):
        rows = db.execute("SELECT * FROM v_analytics_by_month").fetchall()
        return [dict(r._mapping) for r in rows]

    def by_category(self, db: Session):
        rows = db.execute("SELECT * FROM v_analytics_by_category").fetchall()
        return [dict(r._mapping) for r in rows]

    def by_event(self, db: Session):
        rows = db.execute("SELECT * FROM v_analytics_by_event").fetchall()
        return [dict(r._mapping) for r in rows]

    def utilization(self, db: Session):
        rows = db.execute("SELECT * FROM v_analytics_utilization").fetchall()
        return [dict(r._mapping) for r in rows]

repo_analytics = AnalyticsRepo()
