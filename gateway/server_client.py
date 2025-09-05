import httpx
from typing import Any, Dict, Optional
from gateway.config import settings

class ServerClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def _req(self, method: str, path: str, token: Optional[str] = None, **kw) -> Any:
        headers = kw.pop("headers", {}) or {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=20.0) as c:
            r = await c.request(method, url, headers=headers, **kw)
        if r.status_code >= 400:
            detail = r.text[:300]
            raise httpx.HTTPStatusError(detail, request=r.request, response=r)
        return r.json() if r.headers.get("content-type","").startswith("application/json") else r.text

    async def get(self, path: str, token: Optional[str] = None, params: Optional[Dict]=None):
        return await self._req("GET", path, token=token, params=params)

    async def post(self, path: str, token: Optional[str] = None, json: Optional[Dict]=None):
        return await self._req("POST", path, token=token, json=json)

    async def patch(self, path: str, token: Optional[str] = None, json: Optional[Dict]=None):
        return await self._req("PATCH", path, token=token, json=json)

    async def delete(self, path: str, token: Optional[str] = None):
        return await self._req("DELETE", path, token=token)

server = ServerClient(settings.SERVER_BASE_URL)
