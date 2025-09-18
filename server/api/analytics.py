# server/api/analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from decimal import Decimal

from server.core.deps import get_db
from server.models.analytics import (
    AnalyticsSummary, DashboardTotals,
    ByMonthItem, ByCategoryItem, ByEventItem
)
from server.repositories.analytics_repo import repo_analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ---------- helpers ----------
def _to_int(x):
    if x is None: return 0
    if isinstance(x, Decimal): return int(x)
    try: return int(x)
    except Exception: return 0

def _to_float(x):
    if x is None: return 0.0
    if isinstance(x, Decimal): return float(x)
    try: return float(x)
    except Exception: return 0.0

def _as_percent(x) -> float:
    """Normalize fraction (0..1) to percent (0..100). Leave >1 as-is."""
    val = _to_float(x)
    if val <= 1.0 and val >= 0.0:
        return val * 100.0
    return val


# ---------- mappers ----------
def _map_totals(raw: dict) -> DashboardTotals:
    # capacity_utilization_pct עשוי להגיע כשבר (0..1) מה-View => ננרמל לאחוזים
    cap_util = _as_percent(raw.get("capacity_utilization_pct"))
    return DashboardTotals(
        events_published         = _to_int(raw.get("total_events")),
        registrations_total      = _to_int(raw.get("total_registrations_confirmed")) + _to_int(raw.get("total_waitlist")),
        registrations_confirmed  = _to_int(raw.get("total_registrations_confirmed")),
        registrations_waitlist   = _to_int(raw.get("total_waitlist")),
        capacity_sum             = _to_int(raw.get("capacity_sum")),
        capacity_utilization_pct = cap_util,
        revenue_sum              = (None if raw.get("revenue_sum") is None else _to_float(raw.get("revenue_sum"))),
    )

def _map_by_month(row: dict) -> ByMonthItem:
    # עמודות אפשריות מה-View: ym / month, events / created_events, registrations, registrations_confirmed / confirmed, waitlist, revenue
    month   = row.get("month") or row.get("ym") or ""
    created = row.get("created_events") or row.get("events") or 0
    regs    = row.get("registrations") or 0
    conf    = row.get("confirmed") or row.get("registrations_confirmed") or 0
    wait    = row.get("waitlist") or 0
    rev     = row.get("revenue") if "revenue" in row else row.get("sum_revenue")
    return ByMonthItem(
        month= str(month),
        created_events=_to_int(created),
        registrations =_to_int(regs),
        confirmed     =_to_int(conf),
        waitlist      =_to_int(wait),
        revenue       =(None if rev is None else _to_float(rev)),
    )

def _map_by_category(row: dict) -> ByCategoryItem:
    cat   = row.get("category") or row.get("Category") or ""
    evs   = row.get("events") or row.get("events_count") or 0
    regs  = row.get("registrations") or 0
    conf  = row.get("confirmed") or row.get("registrations_confirmed") or 0
    wait  = row.get("waitlist") or 0
    rev   = row.get("revenue") if "revenue" in row else row.get("sum_revenue")
    return ByCategoryItem(
        category=str(cat),
        events=_to_int(evs),
        registrations=_to_int(regs),
        confirmed=_to_int(conf),
        waitlist=_to_int(wait),
        revenue=(None if rev is None else _to_float(rev)),
    )

def _map_by_event(row: dict) -> ByEventItem:
    eid   = row.get("event_id") or row.get("id") or ""
    title = row.get("title") or row.get("Title") or ""
    cap   = row.get("capacity") or 0
    conf  = row.get("confirmed") or row.get("registrations_confirmed") or 0
    wait  = row.get("waitlist") or 0
    util  = row.get("utilization_pct")
    rev   = row.get("revenue") if "revenue" in row else row.get("sum_revenue")

    # אם אין אחוז ניצולת מוכן – נחשב; אם הגיע כשבר (0..1) – ננרמל ל-0..100
    if util is None:
        util = (_to_float(conf) / _to_float(cap) * 100.0) if _to_int(cap) > 0 else 0.0
    else:
        util = _as_percent(util)

    return ByEventItem(
        event_id=str(eid),
        title=str(title),
        capacity=_to_int(cap),
        confirmed=_to_int(conf),
        waitlist=_to_int(wait),
        utilization_pct=_to_float(util),
        revenue=(None if rev is None else _to_float(rev)),
    )


# ---------- route ----------
@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)):
    totals      = repo_analytics.totals(db)
    by_month    = repo_analytics.by_month(db)
    by_category = repo_analytics.by_category(db)
    by_event    = repo_analytics.by_event(db)
    return AnalyticsSummary(
        totals=_map_totals(totals),
        by_month=[_map_by_month(r) for r in by_month],
        by_category=[_map_by_category(r) for r in by_category],
        top_events=[_map_by_event(r) for r in by_event],
    )
