from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.core.deps import get_db, get_current_user
from server.models.user import User
from server.models.analytics import (
    AnalyticsSummary,
    DashboardTotals,
    ByMonthItem,
    ByCategoryItem,
    ByEventItem,
)
from server.repositories.analytics_repo import repo_analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    totals = repo_analytics.totals(db)
    by_month = repo_analytics.by_month(db)
    by_category = repo_analytics.by_category(db)
    by_event = repo_analytics.by_event(db)
    return AnalyticsSummary(
        totals=DashboardTotals(**totals),
        by_month=[ByMonthItem(**row) for row in by_month],
        by_category=[ByCategoryItem(**row) for row in by_category],
        top_events=[ByEventItem(**row) for row in by_event],
    )
