# gateway/api/analytics.py
from fastapi import APIRouter, HTTPException, Request
import os, requests

router = APIRouter(prefix="/analytics", tags=["analytics"])

SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = int(os.getenv("SERVER_TIMEOUT", "15"))

def _headers(req: Request) -> dict:
    h = {}
    if "authorization" in req.headers:
        h["authorization"] = req.headers["authorization"]
    if "x-request-id" in req.headers:
        h["x-request-id"] = req.headers["x-request-id"]
    return h

@router.get("/summary")
def proxy_analytics_summary(request: Request):
    try:
        r = requests.get(f"{SERVER_BASE_URL}/analytics/summary",
                         headers=_headers(request), timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gateway failed: {e}")
