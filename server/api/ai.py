from fastapi import APIRouter, Depends, HTTPException
import requests

from server.core.deps import get_current_user
from server.models.user import User
from server.models.ai import ChatRequest, ChatResponse
from server.core.config import settings

router = APIRouter(prefix="/ai", tags=["ai"])

def _ollama_available() -> bool:
    try:
        r = requests.get(f"{settings.OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

def _chat_ollama(messages, model: str, timeout: int) -> str:
    payload = {"model": model, "messages": messages, "stream": False}
    r = requests.post(f"{settings.OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"ollama error: {r.text[:200]}")
    data = r.json()
    msg = data.get("message") or {}
    return msg.get("content") or ""

@router.post("/ask", response_model=ChatResponse)
def ask_ai(body: ChatRequest, _: User = Depends(get_current_user)):
    system_prompt = "You are EventHub Assistant. Answer concisely."
    msgs = [{"role": "system", "content": system_prompt}]
    if body.history:
        for m in body.history:
            msgs.append({"role": m.role, "content": m.content})
    msgs.append({"role": "user", "content": body.question})

    if _ollama_available():
        answer = _chat_ollama(
            messages=msgs,
            model=getattr(settings, "AI_MODEL", "llama3"),
            timeout=getattr(settings, "AI_TIMEOUT", 15),
        )
        return ChatResponse(answer=answer or "no answer", used_model=settings.AI_MODEL, from_cache=False)
    return ChatResponse(answer="demo mode: no model connected", used_model="fallback", from_cache=False)
