from __future__ import annotations
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field

AgentRequestStatus = Literal["NEW", "APPROVED", "REJECTED"]

class AgentRequestCreate(BaseModel):
    reason: str = Field(min_length=2, max_length=500)

class AgentRequestPublic(BaseModel):
    id: int
    user_id: int
    status: AgentRequestStatus
    reason: Optional[str] = None
    created_at: datetime
    decided_at: Optional[datetime] = None
    decided_by: Optional[int] = None
