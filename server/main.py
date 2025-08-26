from fastapi import FastAPI
from server.api import books          # ← הוספה

app = FastAPI(title="BookAdvisor API")
app.include_router(books.router)       # ← הוספה

@app.get("/health")
def health():
    return {"ok": True}
