# client/services/users_service.py
import os, requests
BASE = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class UsersService:
    def me(self) -> dict:
        r = requests.get(f"{BASE}/users/me", timeout=12)
        r.raise_for_status()
        return r.json()
    def my_likes(self) -> list:
        r = requests.get(f"{BASE}/reactions/me", params={"type":"LIKE"}, timeout=12)
        r.raise_for_status()
        return r.json() or []
    def patch_me(self, **payload) -> dict:
        r = requests.patch(f"{BASE}/users/me", json=payload, timeout=12)
        r.raise_for_status()
        return r.json()
    def change_password(self, password: str):
        r = requests.post(f"{BASE}/users/me/password", json={"password": password}, timeout=12)
        r.raise_for_status()
        return r.json() if r.content else {}
