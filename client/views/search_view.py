# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Client — SearchView (PySide6)
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
Purpose (Explanation Box)
- Replace hard-coded demo cards with real data fetched from the Gateway (port 9000).
- Clean separation:
    * _fetch_events(...)  -> HTTP GET to the BFF/Gateway
    * _render_events(...) -> Build EventCard widgets from the result
- Resilient UX: shows a friendly message when there are no results or an error occurs.
- Ready for future wiring to details view via the openDetails signal.
"""

from typing import Dict, Any, List, Optional
import requests
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QScrollArea,
)
from PySide6.QtCore import Signal, Qt

# Reusable UI components
from ..ui import SearchBar, EventCard, PageTitle, Muted

GATEWAY_BASE_URL = "http://127.0.0.1:9000"  # BFF/Gateway origin


class SearchView(QWidget):
    # Emits search text + filters dict (if other views want to listen)
    searchRequested = Signal(str, dict)
    # Emits selected event id as string for DetailsView navigation
    openDetails = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # ---- Root layout ----
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 28, 16, 16)
        root.setSpacing(12)

        root.addWidget(PageTitle("חיפוש אירועים"))
        root.addWidget(Muted("מצאי/מצא במהירות לפי שם אמן, עיר או אולם."))

        # ---- Search bar ----
        self.searchbar = SearchBar("שם אמן / עיר / אולם")
        self.searchbar.btn.clicked.connect(self._on_search_clicked)
        root.addWidget(self.searchbar)

        # ---- Quick pills (static UI) ----
        pills_row = QHBoxLayout()
        pills_row.setSpacing(6)
        for t in ["היום", "מחר", 'סופ"ש']:
            lbl = QLabel(t)
            lbl.setObjectName("Pill")
            pills_row.addWidget(lbl)
        pills_row.addStretch(1)
        root.addLayout(pills_row)

        # ---- Results area (scrollable) ----
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self._content = QWidget()
        self._grid = QGridLayout(self._content)
        self._grid.setSpacing(12)
        self._grid.setContentsMargins(4, 4, 4, 4)

        self.scroll.setWidget(self._content)
        root.addWidget(self.scroll, 1)

        # First load (no filters)
        self._load_and_render()

    # ---------------------------
    # Event handlers
    # ---------------------------
    def _on_search_clicked(self) -> None:
        q = self.searchbar.q.text().strip()
        filters = {"city": self.searchbar.city.currentText()}
        self.searchRequested.emit(q, filters)
        self._load_and_render(q, filters)

    # ---------------------------
    # Data fetching
    # ---------------------------
    def _fetch_events(self, q: str = "", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Calls the Gateway BFF and returns a list of event dicts.
        You can switch endpoint here if your BFF shape changes.
        """
        # Option A: dedicated BFF feed (flattened items)
        url = f"{GATEWAY_BASE_URL}/bff/home/feed"
        params = {"q": q or None, "category": None, "page": 1, "limit": 12}

        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json() or {}
            # Expected shape: { total, page, limit, items: [ {id,title,city,starts_at,image_url,...} ], ... }
            items = data.get("items", [])
            return items

        except Exception as e:
            print("⚠️ Error fetching events from Gateway:", e)
            return []

    # ---------------------------
    # Rendering
    # ---------------------------
    def _clear_grid(self) -> None:
        # Remove previous widgets from the grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

    def _safe_date(self, starts_at: Optional[str]) -> str:
        if not starts_at:
            return ""
        # starts_at might be ISO string; show DD/MM format
        try:
            dt = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
            return dt.strftime("%d/%m")
        except Exception:
            # Fallback: take first 10 chars (YYYY-MM-DD) and flip
            s = str(starts_at)[:10]
            if len(s) == 10 and s[4] == "-" and s[7] == "-":
                y, m, d = s.split("-")
                return f"{d}/{m}"
            return s

    def _render_events(self, events: List[Dict[str, Any]]) -> None:
        self._clear_grid()

        if not events:
            # Friendly empty state
            empty = QLabel("לא נמצאו אירועים תואמים ✨")
            empty.setAlignment(Qt.AlignCenter)
            empty.setObjectName("EmptyHint")
            self._grid.addWidget(empty, 0, 0)
            return

        for i, ev in enumerate(events):
            title = ev.get("title") or "ללא כותרת"
            city = ev.get("city") or ""
            venue = city if city else ""
            date = self._safe_date(ev.get("starts_at"))
            price_val = ev.get("price")
            price = f"₪{int(price_val)}" if isinstance(price_val, (int, float)) else ""

            card = EventCard(
                title=title,
                venue=venue,
                date=date,
                price=price,
            )

            # Navigate to details (emit event id)
            ev_id = ev.get("id")
            if ev_id is not None:
                card.details_button.clicked.connect(
                    lambda _, eid=str(ev_id): self.openDetails.emit(eid)
                )

            self._grid.addWidget(card, i // 3, i % 3)

    # ---------------------------
    # Orchestration
    # ---------------------------
    def _load_and_render(self, q: str = "", filters: Optional[Dict[str, Any]] = None) -> None:
        events = self._fetch_events(q, filters)
        self._render_events(events)
