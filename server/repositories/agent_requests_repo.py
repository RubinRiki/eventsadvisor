from __future__ import annotations
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from server.models.db_models import AgentRequestDB, UsersDB  
from server.models.agent_request import AgentRequestCreate, AgentRequestPublic

class AgentRequestsRepo:
    def _to_public(self, r: AgentRequestDB) -> AgentRequestPublic:
        return AgentRequestPublic(
            id=r.Id,
            user_id=r.UserId,
            status=r.status,
            reason=r.reason,
            created_at=r.CreatedAt,
            decided_at=r.DecidedAt,
            decided_by=r.DecidedByUserId,
        )

    def create(self, db: Session, user_id: int, data: AgentRequestCreate) -> AgentRequestPublic:
        obj = AgentRequestDB(UserId=user_id, status="NEW", reason=data.reason)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return self._to_public(obj)

    def list_all(self, db: Session) -> List[AgentRequestPublic]:
        rows = db.query(AgentRequestDB).order_by(AgentRequestDB.CreatedAt.desc()).all()
        return [self._to_public(r) for r in rows]

    def set_status(self, db: Session, req_id: int, status: str, decider_id: int) -> AgentRequestPublic:
        r = db.get(AgentRequestDB, req_id)
        if not r:
            raise ValueError("request not found")
        r.status = status
        r.DecidedAt = datetime.utcnow()
        r.DecidedByUserId = decider_id
        db.commit()
        db.refresh(r)
        return self._to_public(r)

repo_agent_requests = AgentRequestsRepo()
