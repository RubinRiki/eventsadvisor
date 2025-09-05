from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.core.deps import get_db, get_current_user
from server.models.user import User
from server.repositories.analytics_repo import repo_analytics
from server.models.analytics import (
    TotalsSummary, ByMonthSummary, ByCategorySummary, ByEventSummary, UtilizationSummary
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/totals", response_model=TotalsSummary)
def totals(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return repo_analytics.totals(db)

@router.get("/by-month", response_model=list[ByMonthSummary])
def by_month(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return repo_analytics.by_month(db)

@router.get("/by-category", response_model=list[ByCategorySummary])
def by_category(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return repo_analytics.by_category(db)

@router.get("/by-event", response_model=list[ByEventSummary])
def by_event(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return repo_analytics.by_event(db)

@router.get("/utilization", response_model=list[UtilizationSummary])
def utilization(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return repo_analytics.utilization(db)
