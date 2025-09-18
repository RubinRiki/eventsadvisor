# client/views/consult_view.py
import os, requests, asyncio
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Qt
from ..ui import PageTitle, Muted


class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.setObjectName("UserBubble" if is_user else "BotBubble")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(0)
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lay.addWidget(lbl)


class ConsultView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 28, 16, 16)
        root.setSpacing(12)
        root.addWidget(PageTitle("ייעוץ עם הסוכן"))
        root.addWidget(Muted("שוחחי עם הבוט וקבלי תשובות חכמות מבוססות AI."))

        # Scrollable chat area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(8, 8, 8, 8)
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch(1)
        self.scroll.setWidget(self.chat_container)
        root.addWidget(self.scroll, 1)

        # Input row
        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("כתבו שאלה…")
        send = QPushButton("שלח")
        send.setObjectName("Primary")
        row.addWidget(self.input, 1)
        row.addWidget(send)
        root.addLayout(row)

        # הודעת פתיחה מהבוט
        self.add_bot("שלום הדסוש 💙 איך אפשר לעזור?")

        send.clicked.connect(self._send)
        self.input.returnPressed.connect(self._send)

        # סטייל לבועות (אפשר להעביר ל-style_manager)
        self.setStyleSheet(
            """
            QFrame#UserBubble {
                background: #3a4661;
                border: 1px solid #2a3242;
                border-radius: 14px;
            }
            QFrame#BotBubble {
                background: #2f374f;
                border: 1px solid #2a3242;
                border-radius: 14px;
            }
        """
        )

    def add_user(self, text: str):
        bubble = ChatBubble(text, True)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(bubble)  # ימין
        wrapper = QWidget()
        wrapper.setLayout(row)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, wrapper)
        self._scroll_bottom()

    def add_bot(self, text: str):
        bubble = ChatBubble(text, False)
        row = QHBoxLayout()
        row.addWidget(bubble)
        row.addStretch(2)
        wrapper = QWidget()
        wrapper.setLayout(row)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, wrapper)
        self._scroll_bottom()

    def _send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.add_user(text)
        self.input.clear()
        # הוספת "כותב..." זמני
        self.add_bot("הבוט כותב...")
        asyncio.create_task(self.ask_ai(text))

    async def ask_ai(self, text: str):
        try:
            url = f"{os.getenv('GATEWAY_BASE_URL','http://127.0.0.1:9000')}/ai/ask"
            r = requests.post(url, json={"question": text}, timeout=20)
            r.raise_for_status()
            data = r.json()
            answer = data.get("answer", "❌ לא התקבלה תשובה מהבוט")
            self.add_bot(answer)
        except Exception as e:
            self.add_bot(f"שגיאה: {e}")

    def _scroll_bottom(self):
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )
