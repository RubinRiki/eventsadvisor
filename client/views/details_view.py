# client/views/details_view.py
# -*- coding: utf-8 -*-
import os, requests
from threading import Thread
from datetime import datetime

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
)

from ..ui import Card, SectionTitle, PageTitle, Muted

GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")


class DetailsView(QWidget):
    """
    עמוד פרטי אירוע קומפקטי עם לייק/ביטול לייק:
    - כותרת + מטא (מיקום/תאריך/מחיר)
    - כרטיס "על האירוע" עם תיאור
    - פעולות: קנייה / שיתוף / לייק (Toggle)
    - טעינה אסינכרונית מ-Gateway
    """

    # אותות בין threads ל-GUI:
    _dataReady = Signal(dict)   # נתוני אירוע
    _likeState = Signal(dict)   # {"phase": "loading|liked|unliked|error", "code": int|None, "msg": str|None}
    _notify    = Signal(str, str, int)  # title, text, icon (QMessageBox.Icon.value)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)

        # ===== שורש העמוד – מרווחים מינימליים =====
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)   
        root.setSpacing(4)

        # ===== כותרות – טקסט מעט גדול ומרווח קטן =====
        self.title = PageTitle("שם אירוע · דמו")
        self.title.setStyleSheet("font-size: 20px; margin-bottom: 2px;")
        self.meta  = Muted("מיקום · תאריך · מחיר")
        self.meta.setStyleSheet("font-size: 13px;")

        root.addWidget(self.title)
        root.addWidget(self.meta)

        # ===== כרטיס מידע – מרווחים קטנים =====
        info = Card()
        il = QVBoxLayout(info)
        il.setContentsMargins(10, 10, 10, 10)   # קומפקטי
        il.setSpacing(4)
        il.addWidget(SectionTitle("על האירוע"))

        self.desc  = Muted("תיאור קצר של האירוע…")
        self.desc.setStyleSheet("font-size: 13px;")
        self.extra = QLabel("")            # פרטים משלימים דחוסים
        self.extra.setObjectName("DimText")
        self.extra.setStyleSheet("font-size: 12px;")

        il.addWidget(self.desc)
        il.addWidget(self.extra)
        root.addWidget(info)

        # ===== פעולות – קומפקטי, מיושר לימין =====
        cta = QHBoxLayout()
        cta.setSpacing(6)
        self.btn_buy   = QPushButton("המשך להזמנה"); self.btn_buy.setObjectName("Primary")
        self.btn_share = QPushButton("שתף");         self.btn_share.setObjectName("Secondary")
        self.btn_like  = QPushButton("❤️ לייק");     self.btn_like.setObjectName("Secondary")
        self.btn_like.setStyleSheet("color: white;")  # שיראו בבירור

        cta.addWidget(self.btn_buy)
        cta.addWidget(self.btn_share)
        cta.addWidget(self.btn_like)
        cta.addStretch(1)   # רווח שמאלה (RTL)
        root.addLayout(cta)

        # ===== טעינה =====
        self._loading = QLabel("טוען…")
        self._loading.setAlignment(Qt.AlignCenter)
        self._loading.setObjectName("LoadingOverlay")
        self._show_loading(False)  # מוסתר כברירת מחדל
        root.addWidget(self._loading)

        # ===== מצב =====
        self._event_id: int | None = None
        self._liked: bool = False

        # ===== wiring =====
        self._dataReady.connect(self._apply_event)
        self._likeState.connect(self._on_like_state)
        self._notify.connect(self._on_notify)
        self.btn_like.clicked.connect(self._handle_like_clicked)

        # שמירה על תוכן “למעלה”, בלי “בטן” ריקה באמצע
        # (הפריסה כבר דוחפת מלמעלה; אין צורך ב-stretch בסוף)

    # ==========================
    # Utils
    # ==========================
    def _show_loading(self, on: bool):
        self._loading.setVisible(on)

    def _fmt_date(self, iso: str | None) -> str:
        if not iso:
            return ""
        try:
            dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
            return dt.strftime("%d/%m/%Y")
        except Exception:
            return str(iso)[:10]

    def _headers(self) -> dict:
        h = {}
        tok = os.getenv("AUTH_TOKEN")  # Bearer <JWT>
        if tok:
            h["Authorization"] = tok
        return h

    # ==========================
    # Public API
    # ==========================
    def set_event(self, title: str, meta: str, description: str, extra: str = ""):
        self.title.setText(title)
        self.meta.setText(meta)
        self.desc.setText(description or "—")
        self.extra.setText(extra)

    def load_event(self, event_id: str | int) -> None:
        """
        GET {GATEWAY_BASE_URL}/events/{id}
        """
        self._event_id = int(event_id)
        self._show_loading(True)
        self._likeState.emit({"phase": "loading", "code": None, "msg": None})

        def _work():
            try:
                r = requests.get(f"{GATEWAY_BASE_URL}/events/{event_id}", timeout=10)
                r.raise_for_status()
                data = r.json() or {}
            except Exception as e:
                data = {"title": "שגיאה בטעינת אירוע", "description": str(e), "_error": True}
            self._dataReady.emit(data)

        Thread(target=_work, daemon=True).start()

    # ==========================
    # Render / Apply (GUI)
    # ==========================
    @Slot(dict)
    def _apply_event(self, data: dict):
        title = data.get("title") or "ללא כותרת"
        city  = data.get("city") or ""
        venue = data.get("venue") or ""
        date  = self._fmt_date(data.get("starts_at"))
        pv    = data.get("price")
        price = f" · החל מ־₪{int(pv)}" if isinstance(pv, (int, float)) else ""

        location = " · ".join(x for x in [venue, city] if x)
        meta     = " · ".join(x for x in [location or None, date or None] if x) + price
        desc     = data.get("description") or "—"

        extra_fields = []
        if venue: extra_fields.append(f"אולם: {venue}")
        if city:  extra_fields.append(f"עיר: {city}")
        if date:  extra_fields.append(f"תאריך: {date}")
        if isinstance(pv, (int, float)): extra_fields.append(f"מחיר: ₪{int(pv)}")
        extra_txt = " | ".join(extra_fields)

        if data.get("id"):
            try:
                self._event_id = int(data["id"])
            except Exception:
                pass

        self.set_event(title, meta, desc, extra=extra_txt)
        self._show_loading(False)

        # אתחול מצב לייק (אם אפשר)
        self._init_like_state()

    # ==========================
    # Like / Unlike
    # ==========================
    def _init_like_state(self):
        if not self._event_id:
            self._likeState.emit({"phase": "unliked", "code": None, "msg": None})
            return

        headers = self._headers()

        def _work():
            # נבדוק אם כבר יש לייק לאירוע הזה
            try:
                url = f"{GATEWAY_BASE_URL}/reactions/me"
                params = {"type": "LIKE", "event_id": self._event_id}
                r = requests.get(url, headers=headers, params=params, timeout=8)
                if r.status_code == 200:
                    js = r.json()
                    liked = False
                    if isinstance(js, dict) and "liked" in js:
                        liked = bool(js.get("liked"))
                    elif isinstance(js, list):
                        liked = any(str(x.get("event_id")) == str(self._event_id) for x in js)
                    self._likeState.emit({"phase": "liked" if liked else "unliked", "code": None, "msg": None})
                    return
            except Exception:
                pass
            self._likeState.emit({"phase": "unliked", "code": None, "msg": None})

        self._likeState.emit({"phase": "loading", "code": None, "msg": None})
        Thread(target=_work, daemon=True).start()

    def _handle_like_clicked(self):
        if not self._event_id:
            return
        # Toggle: אם כרגע לייק -> נבטל; אחרת נעשה לייק
        self._likeState.emit({"phase": "loading", "code": None, "msg": None})
        if self._liked:
            self._do_unlike()
        else:
            self._do_like()

    def _do_like(self):
        def _work():
            try:
                payload = {"event_id": self._event_id, "type": "LIKE"}
                r = requests.post(f"{GATEWAY_BASE_URL}/reactions",
                                  headers=self._headers(), json=payload, timeout=10)
                # 200/201/204 = הצלחה; 409 (כבר קיים) נחשב כהצלחה
                if r.status_code in (200, 201, 204, 409):
                    self._likeState.emit({"phase": "liked", "code": None, "msg": None})
                else:
                    self._likeState.emit({"phase": "error", "code": r.status_code, "msg": r.text or "פעולת לייק נכשלה"})
            except requests.HTTPError as e:
                code = e.response.status_code if e.response is not None else 0
                self._likeState.emit({"phase": "error", "code": code, "msg": "פעולת לייק נכשלה"})
            except Exception as e:
                self._likeState.emit({"phase": "error", "code": None, "msg": f"נכשלה פעולת הלייק: {e}"})
        Thread(target=_work, daemon=True).start()

    def _do_unlike(self):
        def _work():
            try:
                headers = self._headers()
                url = f"{GATEWAY_BASE_URL}/reactions"
                try:
                    r = requests.delete(url, headers=headers, json={"event_id": self._event_id, "type": "LIKE"}, timeout=10)
                except TypeError:
                    r = requests.delete(url, headers=headers, params={"event_id": self._event_id, "type": "LIKE"}, timeout=10)

                if r.status_code in (200, 204, 404):
                    # גם אם 404 (לא היה לייק) – מבחינת UI אנחנו "לא אוהבים"
                    self._likeState.emit({"phase": "unliked", "code": None, "msg": None})
                else:
                    self._likeState.emit({"phase": "error", "code": r.status_code, "msg": r.text or "ביטול לייק נכשל"})
            except requests.HTTPError as e:
                code = e.response.status_code if e.response is not None else 0
                self._likeState.emit({"phase": "error", "code": code, "msg": "ביטול לייק נכשל"})
            except Exception as e:
                self._likeState.emit({"phase": "error", "code": None, "msg": f"ביטול לייק נכשל: {e}"})
        Thread(target=_work, daemon=True).start()

    # ==========================
    # Slots (GUI)
    # ==========================
    @Slot(dict)
    def _on_like_state(self, st: dict):
        phase = st.get("phase")
        code  = st.get("code")
        msg   = st.get("msg")

        if phase == "loading":
            self.btn_like.setText("טוען…")
            self.btn_like.setEnabled(False)
            return

        if phase == "liked":
            self._liked = True
            self.btn_like.setText("💔 ביטול לייק")
            self.btn_like.setEnabled(True)
            return

        if phase == "unliked":
            self._liked = False
            self.btn_like.setText("❤️ לייק")
            self.btn_like.setEnabled(True)
            return

        if phase == "error":
            # נחזיר למצב קודם
            self.btn_like.setEnabled(True)
            if code in (401, 403):
                self._notify.emit(
                    "לא מחובר/ת",
                    "כדי לעשות לייק צריך להתחבר.\nחזרי למסך ההתחברות והיכנסי מחדש.",
                    QMessageBox.Icon.Information.value
                )
            else:
                self._notify.emit(
                    "שגיאה",
                    msg or (f"שגיאה (HTTP {code}) בפעולת לייק"),
                    QMessageBox.Icon.Warning.value
                )
            if not self._liked:
                self.btn_like.setText("❤️ לייק")

    @Slot(str, str, int)
    def _on_notify(self, title: str, text: str, icon_val: int):
        # הצגת הודעה תמיד ב-GUI Thread
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon(icon_val))
            msg.setWindowTitle(title)
            msg.setText(text)
            msg.exec()
        except Exception:
            print(f"[{title}] {text}")
