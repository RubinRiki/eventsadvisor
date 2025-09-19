# client/services/events_service.py
import os, requests
BASE = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class EventsService:
    def search(self, q: str = "", **params) -> list:
        p = {"q": q or None, "page": 1, "limit": 12, **params}
        r = requests.get(f"{BASE}/events/search", params=p, timeout=10)
        r.raise_for_status()
        return (r.json() or {}).get("items", [])

    def get_event(self, event_id: int) -> dict:
        r = requests.get(f"{BASE}/events/{event_id}", timeout=10)
        r.raise_for_status()
        return r.json() or {}

    def is_liked(self, event_id: int) -> bool:
        r = requests.get(f"{BASE}/reactions/me", params={"type": "LIKE", "event_id": event_id}, timeout=8)
        if r.status_code == 200:
            js = r.json()
            if isinstance(js, dict) and "liked" in js: return bool(js["liked"])
            if isinstance(js, list): return any(str(x.get("event_id")) == str(event_id) for x in js)
        return False

    def like(self, event_id: int) -> None:
        r = requests.post(f"{BASE}/reactions", json={"event_id": event_id, "type": "LIKE"}, timeout=10)
        if r.status_code not in (200, 201, 204, 409): r.raise_for_status()

    def unlike(self, event_id: int) -> None:
        try:
            r = requests.delete(f"{BASE}/reactions", json={"event_id": event_id, "type": "LIKE"}, timeout=10)
        except TypeError:
            r = requests.delete(f"{BASE}/reactions", params={"event_id": event_id, "type": "LIKE"}, timeout=10)
        if r.status_code not in (200, 204, 404): r.raise_for_status()
