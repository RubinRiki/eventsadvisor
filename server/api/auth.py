# server/api/auth.py
from fastapi import APIRouter, Depends, HTTPException
import pyodbc
from server.models.user import UserCreate, UserPublic, UserLogin, Token
from server.repositories.users_repo import repo_users
from server.core.jwt import create_access_token
from server.core.security import verify_password
from server.core.deps import get_current_user
from server.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

# ---------- Register ----------
@router.post("/register", response_model=UserPublic, status_code=201)
def register(data: UserCreate):
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        hashed = pwd_context.hash(data.password)
        user = repo_users.create(data, hashed)
        return UserPublic.model_validate(user.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except pyodbc.IntegrityError as e:
        msg = str(e.args)
        if "2601" in msg or "2627" in msg:
            if "IX_Users_email" in msg or "Email" in msg:
                raise HTTPException(status_code=400, detail="email already exists")
            if "IX_Users_Username" in msg or "Username" in msg:
                raise HTTPException(status_code=400, detail="username already exists")
            raise HTTPException(status_code=400, detail="duplicate value")
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal error")


# ---------- Login ----------
@router.post("/login", response_model=Token)
def login(data: UserLogin):
    user = repo_users.get_by_email(data.email.lower())
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = create_access_token(sub=user.email, role=user.role)
    return Token(access_token=token, token_type="bearer")


# ---------- Current User ----------
@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    return UserPublic.model_validate(current_user.model_dump())
