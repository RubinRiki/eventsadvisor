from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.core.deps import get_db, get_current_user
from server.core.config import settings
from server.models.user import User
from server.models.ai import ChatRequest, ChatResponse
import requests

router = APIRouter(prefix="/ai", tags=["ai"])

def _build_messages(body: ChatRequest) -> list[dict]:
    if getattr(body, "history", None):
        return [{"role": m.role, "content": m.content} for m in body.history]
    if getattr(body, "messages", None):
        return [{"role": m.role, "content": m.content} for m in body.messages]
    if getattr(body, "question", None):
        return [{"role": "user", "content": body.question}]
    return []

@router.post("/ask", response_model=ChatResponse)
def ask_ai(
    body: ChatRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    model_name = settings.AI_MODEL
    url = f"{settings.OLLAMA_URL.rstrip('/')}/api/chat"
    payload = {
        "model": model_name,
        "messages": _build_messages(body),
        "stream": False,
    }
    try:
        r = requests.post(url, json=payload, timeout=settings.AI_TIMEOUT)
    except requests.RequestException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable") from e
    if r.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service error")
    data = r.json() or {}
    answer = ""
    if isinstance(data.get("message"), dict):
        answer = data["message"].get("content", "")
    if not answer and "response" in data:
        answer = data.get("response", "")
    if not answer:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="invalid AI response")
    return ChatResponse(answer=answer, used_model=model_name)
