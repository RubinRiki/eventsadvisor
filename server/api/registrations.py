from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.core.deps import get_db, get_current_user, require_any
from server.models.user import User
from server.models.registration import RegistrationCreate, RegistrationPublic
from server.repositories.registrations_repo import repo_registrations

router = APIRouter(prefix="/registrations", tags=["registrations"])

@router.post("", response_model=RegistrationPublic, status_code=status.HTTP_201_CREATED)
def create_registration(
    body: RegistrationCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return repo_registrations.create(db, user_id=int(current.id), data=body)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))

@router.delete("/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_registration(
    registration_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reg = repo_registrations.get(db, registration_id)
    if not reg:
        raise HTTPException(status_code=404, detail="registration not found")

    is_owner = int(reg.user_id) == int(current.id)
    is_privileged = current.role in ("AGENT", "ADMIN")
    if not (is_owner or is_privileged):
        raise HTTPException(status_code=403, detail="forbidden")

    repo_registrations.cancel(db, registration_id)
    return

@router.get("/me", response_model=List[RegistrationPublic])
def list_my_registrations(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return repo_registrations.list_for_user(db, user_id=int(current.id))

@router.get("/event/{event_id}", response_model=List[RegistrationPublic])
def list_event_registrations(
    event_id: int,
    current: User = Depends(require_any("AGENT", "ADMIN")),
    db: Session = Depends(get_db),
):
    return repo_registrations.list_for_event(db, event_id=event_id, requester=current)
