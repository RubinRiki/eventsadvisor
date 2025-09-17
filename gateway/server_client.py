# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Client — gateway/server_client.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
Typed async HTTP client for the frontend "gateway" layer.

Highlights:
- Centralizes HTTP requests (GET/POST/PATCH/DELETE) with optional JWT.
- Joins paths safely with the configured SERVER_BASE_URL.
- Returns JSON if available, otherwise text (or None for empty body).
- Raises meaningful httpx.HTTPStatusError with short detail.

How to use:
    from .server_client import server
    data = await server.get("/health")

Notes:
- Keep requests async-friendly (httpx.AsyncClient).
- Prefer calling with leading slash (e.g., "/auth/login"); the client normalizes it anyway.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Mapping

import httpx

# ✅ Relative import from gateway package
from .config import settings, api_base


class ServerClient:
    """Small async wrapper around httpx for calling the backend API."""

    def __init__(self, base_url: str, *, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _req(
        self,
        method: str,
        path: str,
        *,
        token: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
        **kw: Any,
    ) -> Any:
        # Merge/prepare headers
        hdrs: Dict[str, str] = dict(headers or {})
        if token:
            hdrs["Authorization"] = f"Bearer {token}"

        # Normalize URL
        rel = path.lstrip("/")
        url = f"{self.base_url}/{rel}"

        async with httpx.AsyncClient(timeout=self.timeout) as c:
            r = await c.request(method.upper(), url, headers=hdrs, **kw)

        # Error handling with concise detail
        if r.status_code >= 400:
            detail = None
            # Try to extract a short message
            try:
                j = r.json()
                detail = j.get("detail") or j
            except Exception:
                detail = (r.text or "")[:300]
            raise httpx.HTTPStatusError(str(detail), request=r.request, response=r)

        # Return JSON if content-type indicates JSON; otherwise text/None
        ctype = (r.headers.get("content-type") or "").lower()
        if not r.content:
            return None
        if "application/json" in ctype:
            return r.json()
        return r.text

    # ------------- Public verbs -------------
    async def get(
        self,
        path: str,
        *,
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        return await self._req("GET", path, token=token, params=params, headers=headers)

    async def post(
        self,
        path: str,
        *,
        token: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        return await self._req("POST", path, token=token, json=json, headers=headers)

    async def patch(
        self,
        path: str,
        *,
        token: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        return await self._req("PATCH", path, token=token, json=json, headers=headers)

    async def delete(
        self,
        path: str,
        *,
        token: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        return await self._req("DELETE", path, token=token, headers=headers)


# Singleton client for the app
server = ServerClient(str(settings.SERVER_BASE_URL))
