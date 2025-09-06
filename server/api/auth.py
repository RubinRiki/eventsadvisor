from fastapi import APIRouter, HTTPException, status
from server.models.user import UserCreate, UserLogin, Token, UserPublic
from server.repositories.users_repo import repo_users
from server.core.security import hash_password, verify_password
from server.core.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate):
    if repo_users.get_by_email(body.email):
        raise HTTPException(status_code=400, detail="email already exists")
    pwd_hash = hash_password(body.password)
    user = repo_users.create(body, pwd_hash, role="USER")
    return UserPublic(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        agent_status=getattr(user, "agent_status", "NONE"),
        is_active=user.is_active,
    )

@router.post("/login", response_model=Token)
def login(body: UserLogin):
    user = repo_users.get_by_email(body.email)
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token(sub=user.email, role=user.role)
    return Token(access_token=token)
