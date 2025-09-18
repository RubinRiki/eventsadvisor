# gateway/api/events.py
from fastapi import APIRouter, HTTPException, Request
import os, requests

router = APIRouter(prefix="/events", tags=["events"])

SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = int(os.getenv("SERVER_TIMEOUT", "15"))

def _headers(req: Request) -> dict:
    h = {}
    if "authorization" in req.headers:
        h["authorization"] = req.headers["authorization"]
    if "x-request-id" in req.headers:
        h["x-request-id"] = req.headers["x-request-id"]
    return h

# gateway/api/events.py
@router.get("/search")
def proxy_events_search(request: Request,
                        q: str | None = None,
                        category: str | None = None,
                        from_date: str | None = None,   # ← חדש
                        to_date: str | None = None,     # ← חדש
                        page: int = 1,
                        limit: int = 12):
    params = {"q": q, "category": category, "page": page, "limit": limit,
              "from_date": from_date, "to_date": to_date}  # ← יעבור הלאה
    try:
        r = requests.get(f"{SERVER_BASE_URL}/events/search",
                         params=params, headers=_headers(request), timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gateway failed: {e}")

@router.get("/{event_id}")
def proxy_event_details(event_id: int, request: Request):
    try:
        r = requests.get(f"{SERVER_BASE_URL}/events/{event_id}",
                         headers=_headers(request), timeout=TIMEOUT)
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Event not found")
        r.raise_for_status()
        return r.json()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gateway failed: {e}")
