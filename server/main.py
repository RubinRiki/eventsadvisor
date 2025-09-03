# server/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# ראוטרים
from server.api import auth, orders, events_public, events  # events_public = DB, events = gateway
from server.api import ai as ai_router

# 1) טוען משתני סביבה (.env)
load_dotenv()

app = FastAPI(title="EventAdvisor API")

# 2) CORS (אפשר לצמצם origins בהמשך)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) רישום ראוטרים (ללא חפיפות!)

# ✅ API של ה־DB (טבלת Events ב-Somee)
# שימי לב: אם בתוך events_public.py כבר מוגדר prefix="/events",
# אין צורך להוסיף כאן prefix. השורה הבאה משאירה אותו כפי שהוא.
app.include_router(events_public.router)

# ✅ Auth / Orders
app.include_router(auth.router)    # /auth/*
app.include_router(orders.router)  # /orders/*
app.include_router(ai_router.router)


# ✅ Gateway (Ticketmaster/demo) תחת prefix מובחן
# אם בתוך events.py ה־router מוגדר עם prefix="/events",
# אז כאן מספיק prefix="/tm" והתוצאה תהיה /tm/events/*
app.include_router(events.router, prefix="/tm", tags=["events-gateway"])

# ❌ אל תוסיפי כאן app.include_router(events.router) ללא prefix,
# אחרת ה-gateway ייתפס גם על /events/* ויגנוב נתיבים מה-DB.

# 4) Healthcheck
@app.get("/health")
def health():
    return {
        "ok": True,
        "tm_api_key_loaded": bool(os.getenv("TM_API_KEY")),
        "env": os.getenv("ENV", "local")
    }
