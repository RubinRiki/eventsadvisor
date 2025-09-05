from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from server.core.deps import get_db, get_current_user
from server.core.security import verify_password
from server.core.jwt import create_access_token
from server.models.user import UserCreate, UserLogin, UserPublic, Token, User
from server.repositories.users_repo import repo_users

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = repo_users.get_by_email(db, payload.email.lower())
    if existing:
        raise HTTPException(status_code=400, detail="email already in use")
    hashed = pwd_context.hash(payload.password)
    user = repo_users.create(db, payload, hashed_password=hashed)
    return UserPublic.model_validate(user.model_dump())

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = repo_users.get_by_email(db, payload.email.lower())
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token(sub=user.email, role=user.role)
    return Token(access_token=token, token_type="bearer")

@router.get("/me", response_model=UserPublic)
def me(current: User = Depends(get_current_user)):
    return UserPublic.model_validate(current.model_dump())
