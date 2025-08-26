from fastapi import APIRouter, Query

router = APIRouter(prefix="/books", tags=["books"])

# דמו זמני עד שנחבר DB/ענן
_FAKE = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "genre": "Software"},
    {"id": 2, "title": "Atomic Habits", "author": "James Clear", "genre": "Self-Help"},
    {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "genre": "Software"},
]

@router.get("/search")
def search(q: str = Query("", description="query string")):
    ql = q.lower()
    return [b for b in _FAKE if ql in b["title"].lower() or ql in b["author"].lower()]
