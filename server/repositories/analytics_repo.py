# server/repositories/analytics_repo.py
from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import text

class AnalyticsRepo:
    def totals(self, db: Session):
        row = db.execute(text("SELECT * FROM v_analytics_totals")).mappings().fetchone()
        if not row:
            return {
                "total_users": 0,
                "total_events": 0,
                "total_registrations_confirmed": 0,
                "total_waitlist": 0,
                "total_likes": 0,
                "total_saves": 0,
                # אופציונלי: capacity_sum, revenue_sum...
            }
        return dict(row)

    def by_month(self, db: Session):
        rows = db.execute(text("SELECT * FROM v_analytics_by_month")).mappings().all()
        return [dict(r) for r in rows]

    def by_category(self, db: Session):
        rows = db.execute(text("SELECT * FROM v_analytics_by_category")).mappings().all()
        return [dict(r) for r in rows]

    def by_event(self, db: Session):
        rows = db.execute(text("SELECT * FROM v_analytics_by_event")).mappings().all()
        return [dict(r) for r in rows]

    def utilization(self, db: Session):
        rows = db.execute(text("SELECT * FROM v_analytics_utilization")).mappings().all()
        return [dict(r) for r in rows]

repo_analytics = AnalyticsRepo()
