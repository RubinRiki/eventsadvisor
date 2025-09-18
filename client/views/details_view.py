# client/views/details_view.py
import os, requests
from threading import Thread
from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from ..ui import Card, SectionTitle, PageTitle, Muted

GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class DetailsView(QWidget):
    _dataReady = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self); root.setContentsMargins(16,28,16,16); root.setSpacing(12)

        self.title = PageTitle("שם אירוע · דמו")
        self.meta  = Muted("מיקום/תאריך/מחיר…")
        root.addWidget(self.title); root.addWidget(self.meta)

        info = Card()
        il = QVBoxLayout(info); il.setContentsMargins(16,16,16,16); il.setSpacing(8)
        il.addWidget(SectionTitle("על האירוע"))
        self.desc = Muted("תיאור קצר של האירוע…")
        il.addWidget(self.desc)
        root.addWidget(info)

        cta = QHBoxLayout()
        buy = QPushButton("המשך להזמנה"); buy.setObjectName("Primary")
        share = QPushButton("שתף");        share.setObjectName("Secondary")
        cta.addWidget(buy); cta.addWidget(share); cta.addStretch(1)
        root.addLayout(cta)

        self._loading = QLabel("טוען…")
        self._loading.setAlignment(Qt.AlignCenter)
        self._loading.setObjectName("LoadingOverlay")
        root.addWidget(self._loading)
        self._show_loading(False)

        self._dataReady.connect(self._apply_event)

    def _show_loading(self, on: bool):
        self._loading.setVisible(on)

    def _fmt_date(self, iso: str | None) -> str:
        if not iso: return ""
        try:
            dt = datetime.fromisoformat(str(iso).replace("Z","+00:00"))
            return dt.strftime("%d/%m/%Y")
        except Exception:
            return str(iso)[:10]

    def set_event(self, title: str, meta: str, description: str):
        self.title.setText(title)
        self.meta.setText(meta)
        self.desc.setText(description)

    def _apply_event(self, data: dict):
        title = data.get("title") or "ללא כותרת"
        city  = data.get("city") or ""
        venue = data.get("venue") or ""
        date  = self._fmt_date(data.get("starts_at"))
        pv    = data.get("price")
        price = f" · החל מ־₪{int(pv)}" if isinstance(pv,(int,float)) else ""
        location = " · ".join(x for x in [venue, city] if x)
        meta = " · ".join(x for x in [location or None, date or None] if x) + price
        desc = data.get("description") or "—"
        self.set_event(title, meta, desc)
        self._show_loading(False)

    def load_event(self, event_id: str | int) -> None:
        """Fetch event details from Gateway and render them safely (with loader)."""
        self._show_loading(True)
        def _work():
            try:
                r = requests.get(f"{GATEWAY_BASE_URL}/events/{event_id}", timeout=10)
                r.raise_for_status()
                data = r.json() or {}
            except Exception as e:
                data = {"title":"שגיאה בטעינת אירוע", "description": str(e)}
            self._dataReady.emit(data)
        Thread(target=_work, daemon=True).start()
