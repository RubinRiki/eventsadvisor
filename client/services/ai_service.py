# client/services/ai_service.py
import os, requests
BASE = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class AIService:
    def ask(self, question: str) -> str:
        r = requests.post(f"{BASE}/ai/ask", json={"question": question}, timeout=20)
        r.raise_for_status()
        js = r.json() or {}
        return js.get("answer", "")
