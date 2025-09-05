from __future__ import annotations
from typing import Callable, Iterable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

# Session factory: try infra.db first; fallback to db module name if different
try:
    from server.infra.db import SessionLocal  # your project may have this
except ImportError:
    from server.db import SessionLocal  # fallback if your factory lives here

from server.core.jwt import decode_access_token
from server.repositories.users_repo import repo_users
from server.models.user import User

_security = HTTPBearer(auto_error=True)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(_security),
    db: Session = Depends(get_db),
) -> User:
    token = creds.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    email = payload["sub"]
    user = repo_users.get_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="inactive or not found")
    return user

def require_role(required: str) -> Callable[[User], User]:
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role != required:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return user
    return _checker

def require_any(*roles: Iterable[str]) -> Callable[[User], User]:
    allowed = set(roles)
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return user
    return _checker
