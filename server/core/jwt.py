import time
import jwt
from typing import Dict
from server.config import settings

ALG = settings.JWT_ALG

def create_access_token(sub: str, role: str = "user", ttl_seconds: int = 60 * 60) -> str:
    now = int(time.time())
    payload: Dict = {"sub": sub, "role": role, "iat": now, "exp": now + ttl_seconds}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALG)

def decode_token(token: str) -> Dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALG])
