# server/models/analytics.py
from pydantic import BaseModel
from typing import List, Optional


# --- Totals / KPI Tiles ---
class DashboardTotals(BaseModel):
    events_published: int
    registrations_total: int
    registrations_confirmed: int
    registrations_waitlist: int
    capacity_sum: int
    capacity_utilization_pct: float
    revenue_sum: Optional[float] = None  # אם משתמשים במחירים


# --- Group By: חודשי ---
class ByMonthItem(BaseModel):
    month: str        # 'YYYY-MM'
    created_events: int
    registrations: int
    confirmed: int
    waitlist: int
    revenue: Optional[float] = None


# --- Group By: קטגוריה ---
class ByCategoryItem(BaseModel):
    category: str
    events: int
    registrations: int
    confirmed: int
    waitlist: int
    revenue: Optional[float] = None


# --- Group By: אירוע ספציפי ---
class ByEventItem(BaseModel):
    event_id: str
    title: str
    capacity: int
    confirmed: int
    waitlist: int
    utilization_pct: float
    revenue: Optional[float] = None


# --- Summary for Dashboard ---
class AnalyticsSummary(BaseModel):
    totals: DashboardTotals
    by_month: List[ByMonthItem]
    by_category: List[ByCategoryItem]
    top_events: List[ByEventItem]


# --- אופציונלי: סדרות לזמן (קו) ---
class RegistrationsTimeseriesPoint(BaseModel):
    date: str       # 'YYYY-MM-DD'
    registrations: int
    confirmed: int
    waitlist: int


class RegistrationsTimeseries(BaseModel):
    points: List[RegistrationsTimeseriesPoint]
