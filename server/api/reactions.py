from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from server.core.deps import get_current_user
from server.models.user import User
from server.models.reaction import ReactionCreate, ReactionPublic
from server.repositories.reactions_repo import repo_reactions

router = APIRouter(prefix="/reactions", tags=["reactions"])

@router.post("", response_model=ReactionPublic, status_code=status.HTTP_201_CREATED)
def add_reaction(body: ReactionCreate, current: User = Depends(get_current_user)):
    return repo_reactions.add(user_id=int(current.id), data=body)

@router.delete("/{reaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_reaction(reaction_id: int, current: User = Depends(get_current_user)):
    reaction = repo_reactions.get(reaction_id)
    if not reaction or reaction.user_id != int(current.id):
        raise HTTPException(status_code=404, detail="reaction not found")
    repo_reactions.delete(reaction_id)
    return

@router.get("/event/{event_id}", response_model=List[ReactionPublic])
def list_reactions(event_id: int, current: User = Depends(get_current_user)):
    return repo_reactions.list_for_event(event_id)
