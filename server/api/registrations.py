from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from server.core.deps import get_current_user, require_any
from server.models.user import User
from server.models.registration import RegistrationCreate, RegistrationPublic
from server.repositories.registrations_repo import repo_registrations
from server.repositories.events_repo import repo_events

router = APIRouter(prefix="/registrations", tags=["registrations"])

@router.post("", response_model=RegistrationPublic, status_code=status.HTTP_201_CREATED)
def create_registration(body: RegistrationCreate, current: User = Depends(get_current_user)):
    ev = repo_events.get(body.event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="event not found")
    reg = repo_registrations.create(user_id=int(current.id), data=body)
    return RegistrationPublic.model_validate(reg.model_dump())

@router.delete("/{reg_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_registration(reg_id: int, current: User = Depends(get_current_user)):
    reg = repo_registrations.get(int(reg_id))
    if not reg or reg.user_id != int(current.id):
        raise HTTPException(status_code=404, detail="registration not found")
    repo_registrations.cancel(reg_id=int(reg_id))
    return

@router.get("/my", response_model=List[RegistrationPublic])
def list_my_registrations(current: User = Depends(get_current_user)):
    regs = repo_registrations.list_for_user(int(current.id))
    return [RegistrationPublic.model_validate(r.model_dump()) for r in regs]

@router.get("/event/{event_id}", response_model=List[RegistrationPublic])
def list_for_event(event_id: int, current: User = Depends(require_any("AGENT", "ADMIN"))):
    regs = repo_registrations.list_for_event(event_id=int(event_id), requester=current)
    return [RegistrationPublic.model_validate(r.model_dump()) for r in regs]
