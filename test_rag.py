# test_rag.py
from server.core.deps import get_db
from server.api.rag_service import build_event_index, retrieve_relevant_events

# 1. חיבור ל־DB
db = next(get_db())

# 2. בניית אינדקס מהאירועים
docs = build_event_index(db)
print("📦 מספר אירועים באינדקס:", len(docs))

# 3. הדפסת כמה דוגמאות מהאינדקס
for i, doc in enumerate(docs[:3], 1):
    print(f"--- אירוע {i} ---")
    print(doc)

# 4. בדיקה עם שאלה אמיתית
question = "מה האירועים בתל אביב?"
relevant = retrieve_relevant_events(question, docs, k=3)

print("\n🔎 תוצאות רלוונטיות לשאלה:", question)
for doc in relevant:
    print("✅", doc)
