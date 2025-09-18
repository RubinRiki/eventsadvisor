# client/views/login_view.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional
import os, requests
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
)

SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://127.0.0.1:8000")

class LoginView(QWidget):
    """
    Minimal login form:
      - email + password
      - POST {SERVER_BASE_URL}/auth/login
      - on success emits loggedIn(user_dict)
    """
    loggedIn = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 72, 48, 48); root.setSpacing(12)

        title = QLabel("התחברות")
        title.setObjectName("PageTitle")
        title.setAlignment(Qt.AlignHCenter)
        root.addWidget(title)

        self.email = QLineEdit()
        self.email.setPlaceholderText("אימייל")
        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("סיסמה")
        self.pwd.setEchoMode(QLineEdit.Password)

        self.btn = QPushButton("התחבר/י")
        self.btn.setObjectName("Primary")
        self.btn.clicked.connect(self._on_login)

        self.err = QLabel("")
        self.err.setObjectName("ErrorText")
        self.err.setAlignment(Qt.AlignHCenter)
        self.err.setVisible(False)

        root.addWidget(self.email)
        root.addWidget(self.pwd)
        root.addWidget(self.btn)
        root.addWidget(self.err)

    def _show_error(self, msg: str):
        self.err.setText(msg)
        self.err.setVisible(True)

    def _on_login(self):
        self.err.setVisible(False)
        email = self.email.text().strip()
        password = self.pwd.text().strip()
        if not email or not password:
            self._show_error("יש למלא אימייל וסיסמה")
            return
        try:
            r = requests.post(f"{SERVER_BASE_URL}/auth/login",
                              json={"email": email, "password": password},
                              timeout=10)
            if r.status_code == 401:
                self._show_error("פרטי ההתחברות שגויים")
                return
            r.raise_for_status()
            data = r.json() or {}
            token = data.get("access_token")
            if not token:
                self._show_error("תגובה לא תקינה מהשרת (חסר access_token)")
                return
            # אפשר לשמור את הטוקן ב-os.environ או singleton משותף ל-Client
            # os.environ["AUTH_TOKEN"] = token
            self.loggedIn.emit({"email": email, "token": token})
        except Exception as e:
            self._show_error(f"שגיאה בהתחברות: {e}")
