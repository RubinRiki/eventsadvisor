# server/api/rag_service.py
from server.models.db_models import EventDB
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def build_event_index(db: Session):
    """
    בונה אינדקס של אירועים מה־DB עבור RAG.
    מחזיר רשימה של דיקטים עם טקסט.
    """
    logger.info("🚀 build_event_index התחיל")
    events = db.query(EventDB).all()
    logger.info(f"✅ טענו {len(events)} אירועים מה־DB")

    docs = []
    for e in events:
        try:
            text_parts = []
            if e.Title:
                text_parts.append(f"שם האירוע: {e.Title}")
            if e.City:
                text_parts.append(f"עיר: {e.City}")
            if e.Category:
                text_parts.append(f"קטגוריה: {e.Category}")
            if e.starts_at:
                text_parts.append(f"תאריך התחלה: {e.starts_at}")
            if e.ends_at:
                text_parts.append(f"תאריך סיום: {e.ends_at}")
            if e.description:
                text_parts.append(f"תיאור: {e.description[:200]}...")  # קיצור למניעת טקסט ארוך מדי

            doc_text = " | ".join(text_parts)

            docs.append({
                "id": str(e.Id),
                "text": doc_text
            })
        except Exception as ex:
            logger.warning(f"⚠️ שגיאה בעת עיבוד אירוע {e}: {ex}")

    logger.info(f"📦 אינדקס נבנה עם {len(docs)} מסמכים")
    return docs


def retrieve_relevant_events(query: str, docs: list[dict], k: int = 3):
    """
    חיפוש פשוט בטקסט: מחזיר K אירועים שרלוונטיים לשאילתה
    (בינתיים חיפוש מחרוזת בסיסי).
    """
    logger.info(f"🔎 מחפשים אירועים רלוונטיים לשאילתה: {query}")

    results = []
    for d in docs:
        if query.lower() in d["text"].lower():
            results.append(d)

    logger.info(f"✨ תוצאות רלוונטיות מה־RAG: {results[:k]}")
    return results[:k]
