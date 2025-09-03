from pydantic import BaseModel
from typing import List, Literal, Optional

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    answer: str
    used_model: str
    from_cache: bool = False  # שמור להמשך, כרגע false תמיד
