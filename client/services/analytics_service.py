# client/services/analytics_service.py
import os, requests
BASE = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class AnalyticsService:
    def summary(self) -> dict:
        r = requests.get(f"{BASE}/analytics/summary", timeout=15)
        r.raise_for_status()
        return r.json() or {}
