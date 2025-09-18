# client/views/search_view.py
# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
import os, requests
from datetime import datetime, timedelta
from threading import Thread

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QScrollArea, QPushButton
)

from ..ui import SearchBar, EventCard, PageTitle, Muted

GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class SearchView(QWidget):
    searchRequested = Signal(str, dict)
    openDetails = Signal(str)
    _dataReady = Signal(list)  

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 28, 16, 16); root.setSpacing(12)

        root.addWidget(PageTitle("חיפוש אירועים"))
        root.addWidget(Muted("מצאי/מצא במהירות לפי שם אמן, עיר או אולם."))

        # חיפוש
        self.searchbar = SearchBar("שם אמן / עיר / אולם")
        self.searchbar.btn.clicked.connect(self._on_search_clicked)
        root.addWidget(self.searchbar)

        pills = QHBoxLayout(); pills.setSpacing(6)
        self.btn_today    = self._make_pill("היום")
        self.btn_tomorrow = self._make_pill("מחר")
        self.btn_weekend  = self._make_pill('סופ"ש')
        for b in (self.btn_today, self.btn_tomorrow, self.btn_weekend):
            pills.addWidget(b)
        pills.addStretch(1)
        root.addLayout(pills)

        self.btn_today.clicked.connect(lambda: self._on_quick_date("today"))
        self.btn_tomorrow.clicked.connect(lambda: self._on_quick_date("tomorrow"))
        self.btn_weekend.clicked.connect(lambda: self._on_quick_date("weekend"))
        self._active_range: Optional[tuple[str, str]] = None  # (from_date, to_date)

        # אזור תוצאות
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self._content = QWidget()
        self._grid = QGridLayout(self._content)
        self._grid.setSpacing(12); self._grid.setContentsMargins(4,4,4,4)
        self.scroll.setWidget(self._content)
        root.addWidget(self.scroll, 1)

        # אינדיקציית טעינה
        self._loading = QLabel("טוען…")
        self._loading.setAlignment(Qt.AlignCenter)
        self._loading.setObjectName("LoadingOverlay")
        root.addWidget(self._loading)
        self._show_loading(False)

        # חיבור עדכון נתונים מה־Thread
        self._dataReady.connect(self._render_events)

        # טעינת ברירת מחדל
        self._load_and_render()

    def _make_pill(self, text: str) -> QPushButton:
        b = QPushButton(text)
        b.setObjectName("Pill")
        b.setCheckable(True)
        b.setAutoExclusive(True)
        return b

    # === אירועים ===
    def _on_search_clicked(self) -> None:
        q = self.searchbar.q.text().strip()
        filters = {"city": self.searchbar.city.currentText()}
        
        self._active_range = None
        for b in (self.btn_today, self.btn_tomorrow, self.btn_weekend):
            b.setChecked(False)
        self.searchRequested.emit(q, filters)
        self._load_and_render(q, filters)

    def _on_quick_date(self, which: str) -> None:
        today = datetime.now().date()
        if which == "today":
            f=t=today
        elif which == "tomorrow":
            f=t=today.replace(day=today.day) + timedelta(days=1)
        else:
            # Fri-Sat
            delta_to_fri = (4 - today.weekday()) % 7
            fri = today + timedelta(days=delta_to_fri)
            sat = fri + timedelta(days=1)
            f, t = fri, sat
        self._active_range = (f.isoformat(), t.isoformat())

        q = self.searchbar.q.text().strip()
        filters = {"city": self.searchbar.city.currentText()}
        self.searchRequested.emit(q, filters)
        self._load_and_render(q, filters)

    # === Data ===
    def _fetch_events(self, q: str = "", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        url = f"{GATEWAY_BASE_URL}/events/search"
        params = {"q": q or None, "category": None, "page": 1, "limit": 12}
        if self._active_range:
            params["from_date"], params["to_date"] = self._active_range
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json() or {}
            return data.get("items", [])
        except Exception as e:
            print("⚠️ Error fetching events from Gateway:", e)
            return []

    # === Rendering ===
    def _show_loading(self, on: bool) -> None:
        self._loading.setVisible(on)
        self.scroll.setDisabled(on)

    def _clear_grid(self) -> None:
        while self._grid.count():
            it = self._grid.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None)

    def _safe_date(self, starts_at: Optional[str]) -> str:
        if not starts_at: return ""
        try:
            dt = datetime.fromisoformat(str(starts_at).replace("Z","+00:00"))
            return dt.strftime("%d/%m")
        except Exception:
            s = str(starts_at)[:10]
            if len(s)==10 and s[4]=="-" and s[7]=="-":
                y,m,d = s.split("-")
                return f"{d}/{m}"
            return s

    def _render_events(self, events: List[Dict[str, Any]]) -> None:
        self._show_loading(False)
        self._clear_grid()
        if not events:
            empty = QLabel("לא נמצאו אירועים תואמים ✨")
            empty.setAlignment(Qt.AlignCenter)
            empty.setObjectName("EmptyHint")
            self._grid.addWidget(empty, 0, 0)
            return

        for i, ev in enumerate(events):
            title = ev.get("title") or "ללא כותרת"
            city  = ev.get("city") or ""
            venue = ev.get("venue") or city
            date  = self._safe_date(ev.get("starts_at"))
            pv    = ev.get("price")
            price = f"₪{int(pv)}" if isinstance(pv,(int,float)) else ""
            card = EventCard(title=title, venue=venue, date=date, price=price)

            ev_id = ev.get("id")
            if ev_id is not None:
                card.details_button.clicked.connect(
                    lambda _, eid=str(ev_id): self.openDetails.emit(eid)
                )
            self._grid.addWidget(card, i//3, i%3)

    # === Orchestration ===
    def _load_and_render(self, q: str = "", filters: Optional[Dict[str, Any]] = None) -> None:
        self._show_loading(True)
        # טעינה ברקע כדי שה-UI לא "ייתקע"
        def _work():
            evs = self._fetch_events(q, filters)
            self._dataReady.emit(evs)
        Thread(target=_work, daemon=True).start()
