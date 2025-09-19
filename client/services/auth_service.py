# client/services/auth_service.py
import os, requests
BASE = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class AuthService:
    def login(self, email: str, password: str) -> dict:
        r = requests.post(f"{BASE}/auth/login", json={"email": email, "password": password}, timeout=12)
        r.raise_for_status()
        return r.json()

    def register(self, username: str, email: str, password: str) -> dict:
        r = requests.post(f"{BASE}/auth/register", json={"username": username, "email": email, "password": password}, timeout=12)
        r.raise_for_status()
        return r.json()
