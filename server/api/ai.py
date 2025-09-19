from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.core.deps import get_db
from server.core.config import settings
from server.models.ai import ChatRequest, ChatResponse

import requests
import logging
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
def ask_ai(body: ChatRequest, db: Session = Depends(get_db)):
    print(f"🚀 /ai/ask נקרא עם שאלה: {body.question}")

    model_name = settings.AI_MODEL
    url = f"{settings.OLLAMA_URL.rstrip('/')}/api/chat"
    print(f"📤 URL של Ollama: {url}")
    print(f"⚙️ מודל נבחר: {model_name}")

    # ---------- שלב RAG ----------
    try:
        print("📦 בונים אינדקס מה־DB...")
        docs = build_event_index(db)
        print(f"✅ טענו {len(docs)} אירועים מה־DB")
        relevant = retrieve_relevant_events(body.question, docs, k=3)
        print(f"✨ תוצאות רלוונטיות מה־RAG: {relevant}")
        context_text = "\n\n".join(doc["text"] for doc in relevant)
    except Exception as e:
        logger.error(f"RAG failed: {e}")
        print(f"❌ שגיאה בבניית אינדקס/RAG: {e}")
        context_text = ""

    # מוסיפים context להודעות
    messages = _build_messages(body)
    if context_text:
        system_msg = f"הנה נתוני אירועים רלוונטיים מה־DB:\n{context_text}"
        messages.insert(0, {"role": "system", "content": system_msg})
        print(f"📝 הוספנו context למודל: {system_msg}")

    payload = {"model": model_name, "messages": messages, "stream": False}
    print(f"📦 Payload נשלח ל־Ollama: {payload}")

    # ---------- קריאה ל־Ollama ----------
    try:
        r = requests.post(url, json=payload, timeout=settings.AI_TIMEOUT)
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"AI service unavailable: {e}")
        print(f"❌ שגיאה בחיבור ל־Ollama: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service unavailable",
        )

    try:
        data = r.json() or {}
        print(f"📥 תשובה גולמית מה־Ollama: {data}")
    except Exception as e:
        print(f"❌ שגיאה בפענוח JSON מה־Ollama: {e}")
        raise HTTPException(status_code=502, detail="invalid AI JSON response")

    # ננסה להוציא תשובה
    answer = ""
    if isinstance(data.get("message"), dict):
        answer = data["message"].get("content", "")
    if not answer and "response" in data:
        answer = data.get("response", "")
    if not answer:
        print(f"❌ AI החזיר תשובה לא תקינה: {data}")
        raise HTTPException(status_code=502, detail="invalid AI response")

    print(f"✅ תשובה סופית לצ'אט: {answer}")
    return ChatResponse(answer=answer, used_model=model_name, from_cache=False)
