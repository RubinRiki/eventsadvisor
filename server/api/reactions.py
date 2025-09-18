from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.core.deps import get_db, get_current_user
from server.models.user import UserPublic as User
from server.models.reaction import ReactionCreate, ReactionPublic
from server.repositories.reactions_repo import repo_reactions

router = APIRouter(prefix="/reactions", tags=["reactions"])

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

@router.get("/me", response_model=List[ReactionPublic])
def list_my_reactions(
    type: str = "LIKE",
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return repo_reactions.list_for_user(db, user_id=int(current.id), type=type)