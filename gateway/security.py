from typing import Optional
from fastapi import Cookie, HTTPException, Response
from gateway.config import settings

def get_token(gw_token: Optional[str] = Cookie(default=None, alias=settings.COOKIE_NAME)):
    if not gw_token:
        raise HTTPException(status_code=401, detail="missing token")
    return gw_token

def set_token(resp: Response, token: str):
    resp.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )

def clear_token(resp: Response):
    resp.delete_cookie(key=settings.COOKIE_NAME, path="/")
