# gateway/api/auth.py
from fastapi import APIRouter, HTTPException, Request
import os, requests

router = APIRouter(prefix="/auth", tags=["auth"])
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = int(os.getenv("SERVER_TIMEOUT", "15"))

@router.post("/login")
async def proxy_login(request: Request):
    try:
        payload = await request.json()  # <-- חשוב
        r = requests.post(f"{SERVER_BASE_URL}/auth/login", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)

@router.post("/register")
async def proxy_register(request: Request):
    try:
        payload = await request.json()  # <-- חשוב
        r = requests.post(f"{SERVER_BASE_URL}/auth/register", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)
