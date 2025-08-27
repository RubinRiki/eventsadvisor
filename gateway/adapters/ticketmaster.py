import os, httpx
from typing import Dict, Any, List, Optional

TM_API = "https://app.ticketmaster.com/discovery/v2"
TM_KEY = os.getenv("TM_API_KEY")

def _map_event(ev: Dict[str, Any]) -> Dict[str, Any]:
    # תאריך
    start = ((ev.get("dates") or {}).get("start") or {})
    date = start.get("dateTime") or start.get("localDate")

    # מקום
    venues = ((ev.get("_embedded") or {}).get("venues") or [])
    venue_name = venues[0].get("name") if venues else None
    city = (venues[0].get("city") or {}).get("name") if venues else None
    country = (venues[0].get("country") or {}).get("countryCode") if venues else None

    # מחיר (אם קיים)
    price = None
    for pr in (ev.get("priceRanges") or []):
        mn, mx, cur = pr.get("min"), pr.get("max"), pr.get("currency")
        if mn is not None:
            price = f"{mn}-{mx} {cur}" if mx else f"{mn} {cur}"
            break

    return {
        "id": ev.get("id"),
        "title": ev.get("name"),
        "date": date,
        "venue": venue_name,
        "city": city,
        "country": country,
        "price": price,
        "url": ev.get("url"),
        "source": "ticketmaster",
    }

async def search_events(
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,      # ISO-2: IL/US/...
    latlong: Optional[str] = None,      # "32.0853,34.7818"
    radius: Optional[int] = None,       # ברירת מחדל TM
    unit: Optional[str] = None,         # "km" | "miles"
    startDateTime: Optional[str] = None,# "YYYY-MM-DDTHH:MM:SSZ"
    endDateTime: Optional[str] = None,
    size: int = 10,                     # 1..200 (לרוב)
    page: int = 0,                      # 0-based!
    sort: str = "date,asc",             # חובה לפי TM
) -> Dict[str, Any]:
    if not TM_KEY:
        # דמו בטוח כשאין מפתח
        return {
            "items": [
                {"id": "demo1", "title": "Imagine Dragons", "date": "2025-09-01", "venue": "Yarkon Park", "city": "Tel Aviv", "url": "https://example.com", "source": "demo"},
                {"id": "demo2", "title": "Eyal Golan", "date": "2025-10-12", "venue": "Menora Arena", "city": "Tel Aviv", "url": "https://example.com", "source": "demo"},
            ],
            "total": 2,
            "page": 0,
            "size": 2,
            "has_more": False,
        }

    params = {
        "apikey": TM_KEY,
        "size": str(size),
        "page": str(page),          # 0-based
        "sort": sort,
    }
    if keyword: params["keyword"] = keyword
    if city: params["city"] = city
    if country: params["countryCode"] = country
    if latlong: params["latlong"] = latlong
    if radius: params["radius"] = str(radius or "")
    if unit: params["unit"] = unit
    if startDateTime: params["startDateTime"] = startDateTime
    if endDateTime: params["endDateTime"] = endDateTime

    url = f"{TM_API}/events.json"

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params, headers={"Accept": "application/json", "x-api-key": TM_KEY})
        r.raise_for_status()
        data = r.json()

    events = ((data.get("_embedded") or {}).get("events") or [])
    items = [_map_event(ev) for ev in events]

    page_obj = (data.get("page") or {})
    total_elements = page_obj.get("totalElements", len(items))
    number = page_obj.get("number", page)
    size_used = page_obj.get("size", size)
    total_pages = page_obj.get("totalPages", 1)
    has_more = (number + 1) < total_pages

    return {
        "items": items,
        "total": total_elements,
        "page": number,
        "size": size_used,
        "has_more": has_more,
        "total_pages": total_pages,
    }
