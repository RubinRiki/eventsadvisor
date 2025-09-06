from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from server.models.db_models import ReactionsDB  
from server.models.reaction import ReactionCreate, ReactionPublic

class ReactionsRepo:
    def _to_public(self, r: ReactionsDB) -> ReactionPublic:
        return ReactionPublic(
            id=r.Id,
            user_id=r.UserId,
            event_id=r.EventId,
            type=r.type,
            created_at=r.CreatedAt,
        )

    def add(self, db: Session, user_id: int, data: ReactionCreate) -> ReactionPublic:
        exists = (db.query(ReactionsDB)
                    .filter(ReactionsDB.UserId == user_id,
                            ReactionsDB.EventId == data.event_id,
                            ReactionsDB.type == data.type)
                    .first())
        if exists:
            return self._to_public(exists)

        obj = ReactionsDB(UserId=user_id, EventId=data.event_id, type=data.type)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return self._to_public(obj)


    def get(self, db: Session, reaction_id: int) -> Optional[ReactionPublic]:
        r = db.get(ReactionsDB, reaction_id)
        return self._to_public(r) if r else None

    def delete(self, db: Session, reaction_id: int) -> None:
        r = db.get(ReactionsDB, reaction_id)
        if not r:
            return
        db.delete(r)
        db.commit()

    def list_for_event(self, db: Session, event_id: int) -> List[ReactionPublic]:
        rows = (db.query(ReactionsDB)
                  .filter(ReactionsDB.EventId == event_id)
                  .order_by(ReactionsDB.CreatedAt.desc())
                  .all())
        return [self._to_public(r) for r in rows]

repo_reactions = ReactionsRepo()
