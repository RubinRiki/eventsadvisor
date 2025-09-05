from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class AgentRequest(BaseModel):
    id: str
    user_id: str
    reason: str
    status: Literal["PENDING","APPROVED","REJECTED"] = "PENDING"
    created_at: datetime
    decided_at: datetime | None = None
    decided_by: str | None = None  # admin id