from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from server.core.deps import get_current_user
from server.models.user import User
from server.models.order import RegistrationCreate, Registration
from server.repositories.orders_repo import repo_orders
from server.repositories.events_repo import repo_events

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=Registration, status_code=status.HTTP_201_CREATED)
def create_order(body: RegistrationCreate, current: User = Depends(get_current_user)):
    ev = repo_events.get(body.event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="event not found")
    return repo_orders.create(user_id=current.id, data=body)

@router.get("/{reg_id}", response_model=Registration)
def get_order(reg_id: str, current: User = Depends(get_current_user)):
    reg = repo_orders.get(reg_id)
    if not reg or reg.user_id != current.id:
        raise HTTPException(status_code=404, detail="order not found")
    return reg

@router.get("", response_model=list[Registration])
def list_my_orders(current: User = Depends(get_current_user)):
    return repo_orders.list_for_user(current.id)
