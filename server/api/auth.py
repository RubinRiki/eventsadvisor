from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from server.models.user import UserCreate, UserLogin, UserPublic, Token, User
from server.repositories.users_repo import repo_users
from server.core.security import hash_password, verify_password
from server.core.jwt import create_access_token
from server.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate):
    try:
        user = repo_users.create(body, hashed_password=hash_password(body.password))
        return UserPublic(id=user.id, email=user.email, role=user.role, is_active=user.is_active)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already exists")

@router.post("/login", response_model=Token)
def login(body: UserLogin):
    user = repo_users.get_by_email(body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    token = create_access_token(sub=user.email, role=user.role)
    return Token(access_token=token)

@router.get("/me", response_model=UserPublic)
def me(current: User = Depends(get_current_user)):
    return UserPublic(id=current.id, email=current.email, role=current.role, is_active=current.is_active)
