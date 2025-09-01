from fastapi import FastAPI
<<<<<<< HEAD
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv  # NEW
import os                      # NEW
from server.api import events

# 1) טוען .env (כדי ש-TM_API_KEY ייקלט)
load_dotenv()

app = FastAPI(title="EventAdvisor API")

# 2) CORS – אפשרו ל-GUI מקומי לגשת
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # אפשר לצמצם בהמשך
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) רישום ראוטים
app.include_router(events.router)

@app.get("/health")
def health():
    # עוזר לאבחן אם המפתח נטען
    has_key = bool(os.getenv("TM_API_KEY"))
    return {"ok": True, "tm_api_key_loaded": has_key}
=======
from server.config import settings
from server.api.health import router as health_router
from server.api.auth import router as auth_router
from server.api.events_public import router as events_public_router  
from server.api.orders import router as orders_router 

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(events_public_router)  
app.include_router(orders_router)  

>>>>>>> 6aaa2ca1221d517f3a7f9443f331fbc47a567031
