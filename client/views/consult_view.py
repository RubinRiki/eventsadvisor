# views/consult_view.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt
from ui.components.labels import PageTitle, Muted

class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.setObjectName("UserBubble" if is_user else "BotBubble")
        lay = QVBoxLayout(self); lay.setContentsMargins(12,8,12,8); lay.setSpacing(0)
        lbl = QLabel(text); lbl.setWordWrap(True)
        lay.addWidget(lbl)

class ConsultView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self); root.setContentsMargins(16,28,16,16); root.setSpacing(12)
        root.addWidget(PageTitle("ייעוץ עם הסוכן"))
        root.addWidget(Muted("דמו עיצוב צ׳אט: היינט/שמאל, צבעים שונים."))

        # Scrollable chat area
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container); self.chat_layout.setContentsMargins(8,8,8,8); self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch(1)
        self.scroll.setWidget(self.chat_container)
        root.addWidget(self.scroll, 1)

        # Input row
        row = QHBoxLayout()
        self.input = QLineEdit(); self.input.setPlaceholderText("כתבו שאלה…")
        send = QPushButton("שלח"); send.setObjectName("Primary")
        row.addWidget(self.input, 1); row.addWidget(send)
        root.addLayout(row)

        # דמו: הודעה פתיחה מהבוט
        self.add_bot("שלום! איך אפשר לעזור?")

        send.clicked.connect(self._send)
        self.input.returnPressed.connect(self._send)

        # סטייל לבועות (אפשר לשים גם ב-style_manager אם תרצי)
        self.setStyleSheet("""
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
        """)

    def add_user(self, text: str):
        bubble = ChatBubble(text, True)
        row = QHBoxLayout(); row.addStretch(1); row.addWidget(bubble)  # ימין
        wrapper = QWidget(); wrapper.setLayout(row)
        self.chat_layout.insertWidget(self.chat_layout.count()-1, wrapper)
        self._scroll_bottom()

    def add_bot(self, text: str):
        bubble = ChatBubble(text, False)
        row = QHBoxLayout(); row.addWidget(bubble); row.addStretch(2)  
        wrapper = QWidget(); wrapper.setLayout(row)
        self.chat_layout.insertWidget(self.chat_layout.count()-1, wrapper)
        self._scroll_bottom()

    def _send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.add_user(text)
        self.input.clear()
        self.add_bot("אני בוט דמו. בהמשך אחבר ל-API וניתן תשובות חכמות 😊")

    def _scroll_bottom(self):
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())
