# gateway/api/users.py
from fastapi import APIRouter, HTTPException, Request
import os, requests

router = APIRouter(prefix="/users", tags=["users"])
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = int(os.getenv("SERVER_TIMEOUT", "15"))

def _headers(req: Request) -> dict:
    h = {}
    if "authorization" in req.headers:
        h["authorization"] = req.headers["authorization"]
    return h

@router.patch("/me")
async def proxy_update_me(request: Request):
    try:
        payload = await request.json()
        r = requests.patch(f"{SERVER_BASE_URL}/users/me", headers=_headers(request), json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)

@router.post("/me/password")
async def proxy_change_password(request: Request):
    try:
        payload = await request.json()
        r = requests.post(f"{SERVER_BASE_URL}/users/me/password", headers=_headers(request), json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return {}
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)
