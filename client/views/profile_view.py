# client/views/profile_view.py
# -*- coding: utf-8 -*-
from typing import List, Dict, Any, Optional
import os, requests

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QDialogButtonBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from ..ui import Card, PageTitle, SectionTitle, Muted

GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class ProfileView(QWidget):
    _dataReady = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self); root.setContentsMargins(16,28,16,16); root.setSpacing(12)

        root.addWidget(PageTitle("הפרופיל שלי"))
        root.addWidget(Muted("פרטים בסיסיים + האירועים שאהבתי."))

        # --- כרטיס פרטי משתמש ---
        self.card_profile = Card()
        p = QVBoxLayout(self.card_profile); p.setContentsMargins(16,16,16,16); p.setSpacing(8)
        p.addWidget(SectionTitle("פרטי משתמש"))

        row = QHBoxLayout()
        self.lbl_username = QLabel("—")
        self.lbl_email    = QLabel("—")
        self.lbl_role     = QLabel("—")
        col1 = QVBoxLayout(); col1.addWidget(Muted("Username")); col1.addWidget(self.lbl_username)
        col2 = QVBoxLayout(); col2.addWidget(Muted("Email"));    col2.addWidget(self.lbl_email)
        col3 = QVBoxLayout(); col3.addWidget(Muted("Role"));     col3.addWidget(self.lbl_role)
        row.addLayout(col1); row.addLayout(col2); row.addLayout(col3); row.addStretch(1)
        p.addLayout(row)

        btns = QHBoxLayout()
        self.btn_edit = QPushButton("עריכת פרופיל"); self.btn_edit.setObjectName("Primary")
        self.btn_pass = QPushButton("שינוי סיסמה");   self.btn_pass.setObjectName("Secondary")
        btns.addWidget(self.btn_edit); btns.addWidget(self.btn_pass); btns.addStretch(1)
        p.addLayout(btns)

        # --- כרטיס הלייקים שלי ---
        self.card_likes = Card()
        l = QVBoxLayout(self.card_likes); l.setContentsMargins(16,16,16,16); l.setSpacing(8)
        l.addWidget(SectionTitle("הלייקים שלי"))
        self.likes_table = QTableWidget(0, 2)
        self.likes_table.setHorizontalHeaderLabels(["אירוע", ""])
        self.likes_table.verticalHeader().setVisible(False)
        self.likes_table.setAlternatingRowColors(True)
        self.likes_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        l.addWidget(self.likes_table, 1)

        root.addWidget(self.card_profile)
        root.addWidget(self.card_likes, 1)

        # wiring
        self._dataReady.connect(self._render)
        self.btn_edit.clicked.connect(self._open_edit_dialog)
        self.btn_pass.clicked.connect(self._open_password_dialog)

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
            self.lbl_role.setText("")
            self.likes_table.setRowCount(0)
            return
        if "error" in data:
            self.lbl_username.setText("שגיאה")
            self.lbl_email.setText(str(data["error"]))
            self.lbl_role.setText("")
            self.likes_table.setRowCount(0)
            return

        me = data.get("me") or {}
        likes = data.get("likes") or []

        self.lbl_username.setText(str(me.get("username") or "—"))
        self.lbl_email.setText(str(me.get("email") or "—"))
        self.lbl_role.setText(str(me.get("role") or "USER"))

        rows: List[Dict[str, Any]] = []
        for r in likes:
            eid = r.get("event_id")
            title = f"Event #{eid}"
            rows.append({"event_id": eid, "title": title})

        self.likes_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.likes_table.setItem(i, 0, QTableWidgetItem(row["title"]))
            btn = QPushButton("פרטים")
            btn.setObjectName("Secondary")
            btn.clicked.connect(lambda _=None, eid=row["event_id"]: self._open_event_details(eid))
            self.likes_table.setCellWidget(i, 1, btn)

        self.likes_table.resizeColumnsToContents()
        self.likes_table.horizontalHeader().setStretchLastSection(True)

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
