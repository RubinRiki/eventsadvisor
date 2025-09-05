from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api import auth, events, registrations, agent_requests, reactions, analytics, ai, health
from server.core.config import settings

app = FastAPI(title="EventHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(health.router)

app.include_router(events.router)
app.include_router(registrations.router)
app.include_router(agent_requests.router)
app.include_router(reactions.router)
app.include_router(analytics.router)
