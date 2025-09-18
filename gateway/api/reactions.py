from typing import List
from fastapi import APIRouter, Depends, HTTPException, requests, status
from sqlalchemy.orm import Session

from server.core.deps import get_db, get_current_user
from server.models.user import UserPublic as User
from server.models.reaction import ReactionCreate, ReactionPublic
from server.repositories.reactions_repo import repo_reactions

from fastapi import APIRouter, HTTPException, Request
import os, requests


router = APIRouter(prefix="/reactions", tags=["reactions"])
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = int(os.getenv("SERVER_TIMEOUT", "15"))

@router.post("", response_model=ReactionPublic, status_code=status.HTTP_201_CREATED)
def add_reaction(
    body: ReactionCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return repo_reactions.add(db, user_id=int(current.id), data=body)

@router.delete("/{reaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_reaction(
    reaction_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reaction = repo_reactions.get(db, reaction_id)
    if not reaction or reaction.user_id != int(current.id):
        raise HTTPException(status_code=404, detail="reaction not found")
    repo_reactions.delete(db, reaction_id)
    return

@router.get("/event/{event_id}", response_model=List[ReactionPublic])
def list_reactions(
    event_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return repo_reactions.list_for_event(db, event_id)

def _headers(req: Request) -> dict:
    h = {}
    if "authorization" in req.headers:
        h["authorization"] = req.headers["authorization"]
    return h

@router.get("/me")
def proxy_my_reactions(request: Request):
    try:
        params = dict(request.query_params)
        r = requests.get(f"{SERVER_BASE_URL}/reactions/me", headers=_headers(request), params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)