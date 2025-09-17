from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.core.deps import get_db, get_current_user, require_role
from server.models.user import UserPublic as User
from server.models.agent_request import AgentRequestCreate, AgentRequestPublic
from server.repositories.agent_requests_repo import repo_agent_requests

router = APIRouter(prefix="/agent-requests", tags=["agent-requests"])

@router.post("", response_model=AgentRequestPublic, status_code=status.HTTP_201_CREATED)
def create_agent_request(
    body: AgentRequestCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return repo_agent_requests.create(db, user_id=int(current.id), data=body)

@router.get("", response_model=List[AgentRequestPublic])
def list_requests(
    _: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    return repo_agent_requests.list_all(db)

@router.patch("/{req_id}/approve", response_model=AgentRequestPublic)
def approve_request(
    req_id: int,
    current: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    return repo_agent_requests.set_status(db, req_id, "APPROVED", current.id)

@router.patch("/{req_id}/reject", response_model=AgentRequestPublic)
def reject_request(
    req_id: int,
    current: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    return repo_agent_requests.set_status(db, req_id, "REJECTED", current.id)
