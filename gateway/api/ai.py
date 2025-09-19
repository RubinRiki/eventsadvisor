from fastapi import APIRouter, HTTPException
import httpx
from gateway.core.config import settings

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/ask")
async def ask_ai_proxy(payload: dict):
    """
    פרוקסי לשרת: שולח בקשה ל-/ai/ask ב-Server
    """
    server_url = f"{settings.SERVER_URL.rstrip('/')}/ai/ask"
    print("🔀 Gateway → שולח לשרת:", server_url, "עם payload:", payload)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(server_url, json=payload)
            resp.raise_for_status()
    except httpx.RequestError as e:
        print("❌ Gateway לא הצליח לדבר עם השרת:", e)
        raise HTTPException(status_code=502, detail=f"Gateway error: {e}")

    data = resp.json()
    print("📥 Gateway קיבל חזרה:", data)
    return data
