# client/views/login_view.py
# -*- coding: utf-8 -*-
import os, requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from ..ui import Card, PageTitle, SectionTitle, Muted

GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class LoginView(QWidget):
    loggedIn = Signal()  # נסמן לאפליקציה שנכנסנו

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self); root.setContentsMargins(16,28,16,16); root.setSpacing(12)

        root.addWidget(PageTitle("התחברות"))
        root.addWidget(Muted("היכנסי עם המשתמש הקיים או צרי חשבון חדש."))

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)

        # --- Tab: Login ---
        self.tab_login = Card(); v1 = QVBoxLayout(self.tab_login); v1.setContentsMargins(16,16,16,16); v1.setSpacing(8)
        v1.addWidget(SectionTitle("התחברות"))
        f1 = QFormLayout()
        self.l_email = QLineEdit(); self.l_email.setPlaceholderText("user@example.com")
        self.l_pass  = QLineEdit(); self.l_pass.setEchoMode(QLineEdit.Password)
        f1.addRow("אימייל", self.l_email); f1.addRow("סיסמה", self.l_pass)
        v1.addLayout(f1)

        btn_login = QPushButton("התחברות"); btn_login.setObjectName("Primary")
        btn_login.clicked.connect(self._do_login)
        v1.addWidget(btn_login, 0, Qt.AlignRight)

        # --- Tab: Register ---
        self.tab_reg = Card(); v2 = QVBoxLayout(self.tab_reg); v2.setContentsMargins(16,16,16,16); v2.setSpacing(8)
        v2.addWidget(SectionTitle("הרשמה"))
        f2 = QFormLayout()
        self.r_username = QLineEdit()
        self.r_email    = QLineEdit()
        self.r_pass     = QLineEdit(); self.r_pass.setEchoMode(QLineEdit.Password)
        f2.addRow("שם משתמש", self.r_username)
        f2.addRow("אימייל", self.r_email)
        f2.addRow("סיסמה", self.r_pass)
        v2.addLayout(f2)

        btn_reg = QPushButton("הרשמה"); btn_reg.setObjectName("Secondary")
        btn_reg.clicked.connect(self._do_register)
        v2.addWidget(btn_reg, 0, Qt.AlignRight)

        self.tabs.addTab(self.tab_login, "התחברות")
        self.tabs.addTab(self.tab_reg,   "הרשמה")
        root.addWidget(self.tabs, 1)

    # ---- helpers ----
    def _post(self, path: str, payload: dict):
        r = requests.post(f"{GATEWAY_BASE_URL}{path}", json=payload, timeout=12)
        r.raise_for_status()
        return r.json() if r.content else {}

    def _set_token(self, token: str):
        # שמירה פשוטה ב-ENV (עובד טוב לקליינט דסקטופ). ה-Views קוראים AUTH_TOKEN ושולחים ב-Authorization.
        os.environ["AUTH_TOKEN"] = f"Bearer {token}"

    # ---- actions ----
    def _do_login(self):
        email = self.l_email.text().strip()
        pwd   = self.l_pass.text()
        if not email or not pwd:
            QMessageBox.warning(self, "שגיאה", "חסרים אימייל/סיסמה"); return
        try:
            resp = self._post("/auth/login", {"email": email, "password": pwd})
            token = resp.get("access_token")
            if not token: raise ValueError("no token")
            self._set_token(token)
            self.loggedIn.emit()
        except Exception as e:
            QMessageBox.critical(self, "התחברות נכשלה", str(e))

    def _do_register(self):
        uname = self.r_username.text().strip()
        email = self.r_email.text().strip()
        pwd   = self.r_pass.text()
        if not uname or not email or not pwd:
            QMessageBox.warning(self, "שגיאה", "אנא מלאי שם משתמש, אימייל וסיסמה"); return
        try:
            _ = self._post("/auth/register", {"username": uname, "email": email, "password": pwd})
            QMessageBox.information(self, "הצלחה", "נרשמת בהצלחה! אפשר להתחבר כעת.")
            self.tabs.setCurrentIndex(0)
            self.l_email.setText(email); self.l_pass.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "הרשמה נכשלה", str(e))
