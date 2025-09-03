from fastapi import APIRouter, Depends, HTTPException
from server.core.deps import get_current_user
from server.models.user import User
from server.models.ai import ChatRequest, ChatResponse
from server.config import settings
import requests

router = APIRouter(prefix="/ai", tags=["ai"])

def _ollama_available() -> bool:
    try:
        r = requests.get(f"{settings.OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

def _chat_ollama(messages, model: str, timeout: int) -> str:
    """
    קריאת Chat ל-Ollama בפורמט הסטנדרטי: POST /api/chat
    https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    r = requests.post(f"{settings.OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"ollama error: {r.text[:200]}")
    data = r.json()
    # פורמט טיפוסי: {"message": {"role":"assistant","content":"..."}}
    msg = data.get("message") or {}
    return msg.get("content") or ""

@router.post("/ask", response_model=ChatResponse)
def ask_ai(body: ChatRequest, current: User = Depends(get_current_user)):
    """
    צ'אט פשוט:
    - אם Ollama זמין: ישלח היסטוריה+שאלה ויחזיר תשובה מהמודל.
    - אם לא זמין: תשובת fallback ידידותית.
    """
    system_prompt = (
        "You are EventAdvisor Assistant. Answer concisely in Hebrew when possible. "
        "If the user asks about personal orders or account info, remind that you're server-side."
    )

    # בונים messages בפורמט Ollama
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
        if not answer.strip():
            answer = "לא הצלחתי להפיק תשובה מהמודל כרגע."
        return ChatResponse(answer=answer, used_model=settings.AI_MODEL, from_cache=False)

    # Fallback אם אין Ollama
    fallback = (
        "מצב דמו: אין חיבור למודל כרגע. "
        "אבל זה הפנץ'ליין: נשמר הפורמט, ואת יכולה להחליף ל-Ollama בהמשך."
    )
    return ChatResponse(answer=fallback, used_model="fallback", from_cache=False)
