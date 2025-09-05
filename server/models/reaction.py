from pydantic import BaseModel, Field
from datetime import datetime

class Reaction(BaseModel):
    id: str
    user_id: str
    event_id: str
    kind: str = Field(pattern="^(like|rating)$")
    rating: int | None = None 
    created_at: datetime
