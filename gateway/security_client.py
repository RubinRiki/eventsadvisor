# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Client — gateway/security.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
Utility functions for handling JWT tokens in the *client-side gateway layer*.

Highlights:
- This is NOT FastAPI backend code; here we adapt it for the frontend client.
- Stores and clears tokens via cookies in a consistent way.
- Provides helper methods for managing session cookies.

Notes:
- In a real frontend context, you typically store tokens in memory,
  or in a lightweight secure store (not FastAPI `Response`/`Cookie`).
- For demo/academic purposes, we keep a simplified cookie-based interface.
"""

from typing import Optional

# ✅ Use relative import from the same gateway package
from .config import settings


def get_token(cookies: dict) -> Optional[str]:
    """
    Extract token from cookies dictionary.

    Example:
        token = get_token(request.cookies)
    """
    return cookies.get(settings.COOKIE_NAME)


def set_token(storage: dict, token: str) -> None:
    """
    Set the token in a storage dict (client-side simulation).

    Example:
        set_token(session_storage, "abc123")
    """
    storage[settings.COOKIE_NAME] = token


def clear_token(storage: dict) -> None:
    """
    Remove token from the storage dict.

    Example:
        clear_token(session_storage)
    """
    storage.pop(settings.COOKIE_NAME, None)
