import os
from typing import List, Dict, Optional
from fastapi import APIRouter, Query, HTTPException
import httpx

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/search")
async def search_events(
    q: str = Query("", description="מילת חיפוש: אמן/אירוע/ז׳אנר"),
    city: Optional[str] = Query(None, description="עיר (רשות)"),
    size: int = Query(5, ge=1, le=20, description="כמות תוצאות")
) -> List[Dict]:
    api_key = os.getenv("TM_API_KEY")
    if not api_key:
        # דמו עד שנגדיר מפתח API אמיתי
        return [
            {"id": "demo1", "name": "Imagine Dragons", "date": "2025-09-01", "venue": "Yarkon Park", "price": None, "url": "https://example.com"},
            {"id": "demo2", "name": "Eyal Golan", "date": "2025-10-12", "venue": "Menora Arena", "price": "180-320 ILS", "url": "https://example.com"},
        ]

    params = {"apikey": api_key, "keyword": q or "", "size": str(size)}
    if city:
        params["city"] = city

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get("https://app.ticketmaster.com/discovery/v2/events.json", params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ticketmaster error: {e}")

    events = []
    for ev in (data.get("_embedded", {}) or {}).get("events", []):
        name = ev.get("name")
        date = ((ev.get("dates") or {}).get("start") or {}).get("localDate")
        venues = ((ev.get("_embedded") or {}).get("venues") or [])
        venue = venues[0].get("name") if venues else None
        price = None
        for pr in (ev.get("priceRanges") or []):
            mn, mx, cur = pr.get("min"), pr.get("max"), pr.get("currency")
            if mn is not None:
                price = f"{mn}-{mx} {cur}" if mx else f"{mn} {cur}"
                break
        url = ev.get("url")
        events.append({"id": ev.get("id"), "name": name, "date": date, "venue": venue, "price": price, "url": url})

    return events
