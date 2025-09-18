# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Server — rag_service.py
#  By: Hadas Donat & Riki Rubin
# ================================================================
"""
📌 RAG Service (Retrieval Augmented Generation)
שכבת עזר שמחברת בין DB (אירועים) לבין מודל השפה (Ollama).

שלבים:
1. Build index — מייצרת Embeddings לכל אירוע.
2. Retrieve — חיפוש אירועים רלוונטיים לשאלה (cosine similarity).
3. Inject context — שימוש בתוצאות בשאילתת ה־Chat.
"""

import numpy as np
from sqlalchemy.orm import Session
from server.models.db_models import EventDB
import requests
from server.core.config import settings


# ---------- יצירת Embeddings ----------
def embed_text(text: str) -> list[float]:
    """מייצרת embedding לטקסט בעזרת Ollama"""
    url = f"{settings.OLLAMA_URL.rstrip('/')}/api/embeddings"
    r = requests.post(url, json={"model": settings.AI_MODEL, "prompt": text}, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("embedding", [])


def build_event_index(db: Session) -> list[dict]:
    """בונה אינדקס של כל האירועים מתוך ה־DB"""
    events = db.query(EventDB).all()
    docs = []
    for ev in events:
        text = f"""
        כותרת: {ev.Title}
        קטגוריה: {ev.Category}
        עיר: {ev.City}
        תיאור: {ev.description or ""}
        """
        emb = embed_text(text)
        docs.append({"id": ev.Id, "text": text, "embedding": emb})
    return docs


# ---------- חיפוש אירועים ----------
def cosine_similarity(a: list[float], b: list[float]) -> float:
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def retrieve_relevant_events(query: str, docs: list[dict], k: int = 3) -> list[dict]:
    """מחפש את האירועים הכי קרובים לשאלה"""
    q_emb = embed_text(query)
    scored = [(doc, cosine_similarity(q_emb, doc["embedding"])) for doc in docs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in scored[:k]]
