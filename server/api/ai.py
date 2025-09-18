from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.core.deps import get_db, get_current_user
from server.core.config import settings
from server.models.user import UserPublic as User
from server.models.ai import ChatRequest, ChatResponse

import requests
import logging

# 📌 ייבוא שירותי RAG
from server.api.rag_service import build_event_index, retrieve_relevant_events


router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)


def _build_messages(body: ChatRequest) -> list[dict]:
    messages: list[dict] = []
    if body.history:
        messages.extend({"role": m.role, "content": m.content} for m in body.history)
    if body.question:
        messages.append({"role": "user", "content": body.question})
    return messages


@router.post("/ask", response_model=ChatResponse)
def ask_ai(
    body: ChatRequest,
    db: Session = Depends(get_db),   # 🚨 הורדתי את get_current_user
):
    model_name = settings.AI_MODEL
    url = f"{settings.OLLAMA_URL.rstrip('/')}/api/chat"

    # ---------- שלב RAG ----------
    try:
        docs = build_event_index(db)
        relevant = retrieve_relevant_events(body.question, docs, k=3)
        context_text = "\n\n".join(doc["text"] for doc in relevant)
    except Exception as e:
        logger.error(f"RAG failed: {e}")
        context_text = ""

    # מוסיפים context להודעות
    messages = _build_messages(body)
    if context_text:
        messages.insert(0, {
            "role": "system",
            "content": f"הנה נתוני אירועים רלוונטיים מה־DB:\n{context_text}"
        })

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
    }

    try:
        r = requests.post(url, json=payload, timeout=settings.AI_TIMEOUT)
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"AI service unavailable: {e}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable")

    data = r.json() or {}
    answer = ""
    if isinstance(data.get("message"), dict):
        answer = data["message"].get("content", "")
    if not answer and "response" in data:
        answer = data.get("response", "")
    if not answer:
        logger.error(f"Invalid AI response: {data}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="invalid AI response")

    return ChatResponse(answer=answer, used_model=model_name, from_cache=False)
