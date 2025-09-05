from fastapi import FastAPI, Depends, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from gateway.config import settings
from gateway.server_client import server
from gateway.security import get_token, set_token, clear_token

app = FastAPI(title=settings.APP_NAME)

# CORS (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Auth ----------
class LoginPayload(BaseModel):
    email: EmailStr
    password: str

class RegisterPayload(BaseModel):
    username: str
    email: EmailStr
    password: str

@app.post("/bff/auth/login")
async def bff_login(body: LoginPayload, resp: Response):
    data = await server.post("/auth/login", json=body.model_dump())
    token = data["access_token"]
    set_token(resp, token)
    me = await server.get("/auth/me", token=token)
    return {"token": token, "user": me}

@app.post("/bff/auth/register")
async def bff_register(body: RegisterPayload, resp: Response):
    await server.post("/auth/register", json=body.model_dump())
    login_data = await server.post("/auth/login", json={"email": body.email, "password": body.password})
    token = login_data["access_token"]
    set_token(resp, token)
    me = await server.get("/auth/me", token=token)
    return {"token": token, "user": me}

@app.post("/bff/auth/logout")
async def bff_logout(resp: Response):
    clear_token(resp)
    return {"ok": True}

# ---------- Home / Search ----------
@app.get("/bff/home/feed")
async def bff_home_feed(
    q: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    token: str = Depends(get_token),
):
    events = await server.get("/events/search", token=token, params={"q": q, "category": category, "page": page, "limit": limit})
    totals = await server.get("/analytics/totals", token=token)
    # Slim VM (flatten for client)
    items = [
        {
            "id": e["id"],
            "title": e["title"],
            "category": e.get("category"),
            "city": e.get("city"),
            "starts_at": e.get("starts_at"),
            "image_url": e.get("image_url"),
            "status": e.get("status"),
        }
        for e in events["items"]
    ]
    return {"total": events["total"], "page": events["page"], "limit": events["limit"], "items": items, "totals_summary": totals}

# ---------- Event Details ----------
@app.get("/bff/events/{event_id}")
async def bff_event_details(event_id: int, token: str = Depends(get_token)):
    ev = await server.get(f"/events/{event_id}", token=token)
    regs = await server.get("/registrations/my", token=token)
    my_reg = next((r for r in regs if r["event_id"] == event_id), None)
    return {"event": ev, "my_registration": my_reg}

# ---------- Registrations ----------
class RegistrationPayload(BaseModel):
    event_id: int

@app.post("/bff/registrations")
async def bff_register_event(body: RegistrationPayload, token: str = Depends(get_token)):
    return await server.post("/registrations", token=token, json=body.model_dump())

@app.delete("/bff/registrations/{reg_id}")
async def bff_cancel_registration(reg_id: int, token: str = Depends(get_token)):
    await server.delete(f"/registrations/{reg_id}", token=token)
    return {"ok": True}

# ---------- Profile ----------
@app.get("/bff/profile")
async def bff_profile(token: str = Depends(get_token)):
    me = await server.get("/auth/me", token=token)
    regs = await server.get("/registrations/my", token=token)
    return {"user": me, "registrations": regs}

# ---------- Agent dashboard ----------
@app.get("/bff/agent/dashboard")
async def bff_agent_dashboard(token: str = Depends(get_token)):
    my_events = await server.get("/events/mine/list", token=token)
    by_event = await server.get("/analytics/by-event", token=token)
    rows = []
    for e in my_events:
        s = next((x for x in by_event if x.get("event_id") == e["id"]), None) or {}
        rows.append({
            "event": e,
            "registrations_count": int(s.get("confirmed_count") or 0),
            "waitlist_count": int(s.get("waitlist_count") or 0),
        })
    return {"my_events": rows}

# ---------- Admin dashboard ----------
@app.get("/bff/admin/dashboard")
async def bff_admin_dashboard(token: str = Depends(get_token)):
    agent_requests = await server.get("/agent-requests", token=token)
    totals = await server.get("/analytics/totals", token=token)
    by_category = await server.get("/analytics/by-category", token=token)
    by_month = await server.get("/analytics/by-month", token=token)
    return {
        "agent_requests": agent_requests,
        "totals": totals,
        "by_category": by_category,
        "by_month": by_month,
    }
