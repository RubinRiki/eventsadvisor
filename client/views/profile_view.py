# client/views/profile_view.py
# -*- coding: utf-8 -*-
from typing import List, Dict, Any, Optional
import os, requests

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QDialogButtonBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QSizePolicy, QMessageBox, QFrame, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ..ui import Card, PageTitle, SectionTitle, Muted

GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

def _make_chip(text: str) -> QLabel:
    chip = QLabel(text)
    chip.setObjectName("Chip")
    chip.setAlignment(Qt.AlignCenter)
    chip.setFixedHeight(26)
    chip.setStyleSheet("""
        QLabel#Chip {
            padding: 2px 10px; border-radius: 13px;
            background: rgba(255, 215, 0, 0.16); /* זהוב בהיר */
            color: #FFD700; font-weight: 600;
        }
    """)
    return chip

def _avatar_label(initial: str) -> QLabel:
    lbl = QLabel(initial.upper()[:1] or "U")
    lbl.setFixedSize(56, 56)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet("""
        QLabel {
            border-radius: 28px; background: #2F3645; color: #EAF0FF;
            font-size: 22px; font-weight: 700; letter-spacing: 1px;
        }
    """)
    return lbl

class ProfileView(QWidget):
    _dataReady = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)

        root = QVBoxLayout(self); root.setContentsMargins(16,28,16,16); root.setSpacing(12)
        header = QHBoxLayout(); header.setSpacing(8)
        header.addWidget(PageTitle("הפרופיל שלי"))
        self.btn_refresh = QPushButton("רענון")
        self.btn_refresh.setObjectName("Secondary")
        header.addStretch(1)
        header.addWidget(self.btn_refresh)
        root.addLayout(header)
        root.addWidget(Muted("פרטים בסיסיים + האירועים שאהבתי."))

        # --- כרטיס פרטי משתמש ---
        self.card_profile = Card()
        p = QVBoxLayout(self.card_profile); p.setContentsMargins(16,16,16,16); p.setSpacing(10)
        p.addWidget(SectionTitle("פרטי משתמש"))

        row = QHBoxLayout(); row.setSpacing(16)

        # אוואטר + שם
        self.lbl_avatar = _avatar_label("U")
        col0 = QVBoxLayout()
        col0.addWidget(self.lbl_avatar, alignment=Qt.AlignTop)
        row.addLayout(col0)

        self.lbl_username = QLabel("—")
        self.lbl_username.setFont(QFont(self.font().family(), pointSize=12, weight=QFont.Bold))
        self.lbl_email    = QLabel("—")
        self.lbl_roleChip = _make_chip("USER")

        grid = QVBoxLayout()
        topLine = QHBoxLayout()
        topLine.addWidget(self.lbl_username)
        topLine.addWidget(self.lbl_roleChip)
        topLine.addStretch(1)
        grid.addLayout(topLine)
        grid.addWidget(Muted("Email"))
        grid.addWidget(self.lbl_email)
        row.addLayout(grid, stretch=1)

        # כפתורי פעולה
        btns = QVBoxLayout(); btns.setSpacing(8)
        self.btn_edit = QPushButton("עריכת פרופיל"); self.btn_edit.setObjectName("Primary")
        self.btn_pass = QPushButton("שינוי סיסמה");   self.btn_pass.setObjectName("Secondary")
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_pass)
        btns.addStretch(1)

        row.addLayout(btns)
        p.addLayout(row)

        # קו מפריד דק
        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setStyleSheet("color: rgba(255,255,255,0.08);")
        p.addWidget(sep)

        # --- כרטיס הלייקים שלי ---
        self.card_likes = Card()
        l = QVBoxLayout(self.card_likes); l.setContentsMargins(16,16,16,16); l.setSpacing(8)
        header2 = QHBoxLayout(); header2.addWidget(SectionTitle("הלייקים שלי")); header2.addStretch(1)
        l.addLayout(header2)

        self.likes_table = QTableWidget(0, 2)
        self.likes_table.setHorizontalHeaderLabels(["אירוע", ""])
        self.likes_table.verticalHeader().setVisible(False)
        self.likes_table.setAlternatingRowColors(True)
        self.likes_table.setShowGrid(False)
        self.likes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.likes_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.likes_table.setFocusPolicy(Qt.NoFocus)
        self.likes_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.likes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.likes_table.horizontalHeader().setHighlightSections(False)
        self.likes_table.setStyleSheet("""
            QHeaderView::section { 
                background: rgba(255,255,255,0.06); padding: 6px 8px; border: 0; 
                font-weight: 600;
            }
            QTableWidget { gridline-color: transparent; }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected { background: rgba(88,121,255,0.22); }
        """)
        self.lbl_empty = Muted("אין לייקים עדיין 🙂")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        l.addWidget(self.likes_table, 1)
        l.addWidget(self.lbl_empty)
        self.lbl_empty.hide()

        root.addWidget(self.card_profile)
        root.addWidget(self.card_likes, 1)

        # wiring
        self._dataReady.connect(self._render)
        self.btn_edit.clicked.connect(self._open_edit_dialog)
        self.btn_pass.clicked.connect(self._open_password_dialog)
        self.btn_refresh.clicked.connect(self.reload)

    # ---- public hook for lazy-load ----
    def activate(self):
        self.reload()

    # ---- http helpers ----
    def _headers(self) -> dict:
        h = {}
        tok = os.getenv("AUTH_TOKEN")
        if tok: h["Authorization"] = tok
        return h

    def _get(self, path: str, params: Optional[dict] = None):
        r = requests.get(f"{GATEWAY_BASE_URL}{path}", headers=self._headers(), params=params, timeout=12)
        r.raise_for_status()
        return r.json()

    def _patch(self, path: str, payload: dict):
        r = requests.patch(f"{GATEWAY_BASE_URL}{path}", headers=self._headers(), json=payload, timeout=12)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: dict):
        r = requests.post(f"{GATEWAY_BASE_URL}{path}", headers=self._headers(), json=payload, timeout=12)
        r.raise_for_status()
        return r.json() if r.content else {}

    # ---- load ----
    def reload(self):
        try:
            me = self._get("/users/me")
            likes = self._get("/reactions/me", params={"type": "LIKE"})
            self._dataReady.emit({"me": me, "likes": likes})
        except requests.HTTPError as e:
            code = e.response.status_code if e.response is not None else 0
            if code in (401, 403):
                self._dataReady.emit({"unauthorized": True})
            else:
                self._dataReady.emit({"error": f"{code} {e}"})
        except Exception as e:
            self._dataReady.emit({"error": str(e)})

    # ---- render ----
    def _render(self, data: dict):
        if data.get("unauthorized"):
            self.lbl_username.setText("לא מחובר/ת")
            self.lbl_email.setText("התחברי דרך מסך ההתחברות")
            self.lbl_roleChip.setText("")
            self.lbl_avatar.setText("U")
            self.likes_table.setRowCount(0)
            self.lbl_empty.show()
            return
        if "error" in data:
            self.lbl_username.setText("שגיאה")
            self.lbl_email.setText(str(data["error"]))
            self.lbl_roleChip.setText("")
            self.lbl_avatar.setText("!")
            self.likes_table.setRowCount(0)
            self.lbl_empty.show()
            return

        me = data.get("me") or {}
        likes = data.get("likes") or []

        username = str(me.get("username") or "—")
        self.lbl_username.setText(username)
        self.lbl_email.setText(str(me.get("email") or "—"))
        self.lbl_roleChip.setText(str(me.get("role") or "USER"))
        self.lbl_avatar.setText(username[:1] if username and username != "—" else "U")

        rows: List[Dict[str, Any]] = []
        for r in likes:
            eid = r.get("event_id")
            title = f"Event #{eid}"
            rows.append({"event_id": eid, "title": title})

        self.likes_table.setRowCount(len(rows))
        self.lbl_empty.setVisible(len(rows) == 0)

        for i, row in enumerate(rows):
            item = QTableWidgetItem(row["title"])
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.likes_table.setItem(i, 0, item)

            btn = QPushButton("פרטים")
            btn.setObjectName("Secondary")
            btn.setStyleSheet("color: white;")
            btn.setCursor(Qt.PointingHandCursor)
            # capture current eid
            eid = row["event_id"]
            btn.clicked.connect(lambda _=None, e=eid: self._open_event_details(e))
            self.likes_table.setCellWidget(i, 1, btn)

        self.likes_table.setRowHeight(0, 42) if rows else None
        self.likes_table.resizeColumnsToContents()
        self.likes_table.horizontalHeader().setStretchLastSection(False)

    # ---- dialogs ----
    def _open_edit_dialog(self):
        dlg = QDialog(self); dlg.setWindowTitle("עריכת פרופיל")
        v = QVBoxLayout(dlg); v.setContentsMargins(16,16,16,16); v.setSpacing(8)

        username = QLineEdit(self.lbl_username.text())
        v.addWidget(Muted("Username")); v.addWidget(username)

        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        v.addWidget(bb)
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)

        if dlg.exec() == QDialog.Accepted:
            try:
                self._patch("/users/me", {"username": username.text().strip()})
                self.reload()
            except Exception as e:
                QMessageBox.critical(self, "שגיאה", str(e))

    def _open_password_dialog(self):
        dlg = QDialog(self); dlg.setWindowTitle("שינוי סיסמה")
        v = QVBoxLayout(dlg); v.setContentsMargins(16,16,16,16); v.setSpacing(8)
        pwd = QLineEdit(); pwd.setEchoMode(QLineEdit.Password)
        v.addWidget(Muted("סיסמה חדשה (מינ' 6 תווים)")); v.addWidget(pwd)

        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        v.addWidget(bb)
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)

        if dlg.exec() == QDialog.Accepted:
            try:
                self._post("/users/me/password", {"password": pwd.text()})
                QMessageBox.information(self, "הצלחה", "הסיסמה עודכנה.")
            except Exception as e:
                QMessageBox.critical(self, "שגיאה", str(e))

    # ---- navigation helper ----
    def _open_event_details(self, event_id: int):
        shell = self.window()
        if hasattr(shell, "navigate_to_event"):
            shell.navigate_to_event(event_id)
