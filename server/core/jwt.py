from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError

# Adjust to your settings module if different
try:
    from server.core.config import settings
    SECRET = getattr(settings, "JWT_SECRET", "change-me")
    ALGO = getattr(settings, "JWT_ALGORITHM", "HS256")
    EXPIRES_MIN = int(getattr(settings, "JWT_EXPIRES_MINUTES", 60))
except Exception:
    SECRET = "change-me"
    ALGO = "HS256"
    EXPIRES_MIN = 60

def create_access_token(sub: str, role: str, extra: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    to_encode: Dict[str, Any] = {"sub": sub, "role": role, "iat": int(now.timestamp())}
    if extra:
        to_encode.update(extra)
    expire = now + timedelta(minutes=EXPIRES_MIN)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGO)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])
    except JWTError:
        return None
