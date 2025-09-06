from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime

ReactionType = Literal["LIKE", "SAVE"]

class ReactionCreate(BaseModel):
    event_id: int
    type: ReactionType  # "LIKE" | "SAVE"

class ReactionPublic(BaseModel):
    id: int
    user_id: int
    event_id: int
    type: ReactionType
    created_at: datetime
