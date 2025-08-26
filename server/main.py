from fastapi import FastAPI
from server.api import events

app = FastAPI(title="EventAdvisor API")
app.include_router(events.router)

@app.get("/health")
def health():
    return {"ok": True}
