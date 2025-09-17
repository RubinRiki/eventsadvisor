from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from server.models.db_models import RegistrationDB, EventDB
from server.models.registration import RegistrationCreate, RegistrationPublic, RegistrationStatus
from server.models.user import UserInDB as User

class RegistrationsRepo:
    def _to_public(self, r: RegistrationDB) -> RegistrationPublic:
        return RegistrationPublic(
            id=r.Id,
            user_id=r.UserId,
            event_id=r.EventId,
            status=r.status,
            created_at=r.CreatedAt,
        )

    def _current_confirmed_count(self, db: Session, event_id: int) -> int:
        return db.query(func.count(RegistrationDB.Id)).filter(
            RegistrationDB.EventId == event_id,
            RegistrationDB.status == RegistrationStatus.CONFIRMED
        ).scalar() or 0

    def create(self, db: Session, user_id: int, data: RegistrationCreate) -> RegistrationPublic:
        ev = db.get(EventDB, data.event_id)
        if not ev:
            raise ValueError("event not found")

        confirmed = self._current_confirmed_count(db, data.event_id)
        status = RegistrationStatus.CONFIRMED
        if ev.capacity and confirmed >= ev.capacity:
            status = RegistrationStatus.WAITLIST

        obj = RegistrationDB(UserId=user_id, EventId=data.event_id, status=status)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return self._to_public(obj)

    def get(self, db: Session, reg_id: int) -> Optional[RegistrationPublic]:
        r = db.get(RegistrationDB, reg_id)
        return self._to_public(r) if r else None

    def cancel(self, db: Session, reg_id: int) -> None:
        r = db.get(RegistrationDB, reg_id)
        if not r:
            return
        # cancel
        r.status = RegistrationStatus.CANCELLED
        db.commit()

        # promote next from waitlist if capacity allows
        ev = db.get(EventDB, r.EventId)
        if not ev or not ev.capacity:
            return

        confirmed = self._current_confirmed_count(db, r.EventId)
        if confirmed < ev.capacity:
            next_waiting = (db.query(RegistrationDB)
                              .filter(RegistrationDB.EventId == r.EventId,
                                      RegistrationDB.status == RegistrationStatus.WAITLIST)
                              .order_by(RegistrationDB.CreatedAt.asc())
                              .first())
            if next_waiting:
                next_waiting.status = RegistrationStatus.CONFIRMED
                db.commit()

    def list_for_user(self, db: Session, user_id: int) -> List[RegistrationPublic]:
        rows = (db.query(RegistrationDB)
                  .filter(RegistrationDB.UserId == user_id)
                  .order_by(RegistrationDB.CreatedAt.desc())
                  .all())
        return [self._to_public(r) for r in rows]

    def list_for_event(self, db: Session, event_id: int, requester: User) -> List[RegistrationPublic]:
        rows = (db.query(RegistrationDB)
                  .filter(RegistrationDB.EventId == event_id)
                  .order_by(RegistrationDB.CreatedAt.desc())
                  .all())
        return [self._to_public(r) for r in rows]

repo_registrations = RegistrationsRepo()
