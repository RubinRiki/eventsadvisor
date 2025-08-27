# ui/components/cards.py
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent); self.setObjectName("Card")

class EventCard(Card):
    """כרטיס סטטי לדמו עיצובי"""
    def __init__(self, title="שם אירוע", venue="מקום • עיר", date="12/10", price="₪180", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.setSpacing(6)
        title_lbl = QLabel(title); title_lbl.setStyleSheet("font-weight:800; font-size:16px;")
        meta_lbl  = QLabel(f"{venue} · {date}")
        price_lbl = QLabel(price); price_lbl.setStyleSheet("font-weight:800;")
        btn = QPushButton("פרטים"); btn.setObjectName("Secondary"); btn.setCursor(Qt.PointingHandCursor)
        lay.addWidget(title_lbl); lay.addWidget(meta_lbl); lay.addWidget(price_lbl); lay.addWidget(btn)
        lay.addStretch(1)
        self.details_button = btn
