from fastapi import FastAPI
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

