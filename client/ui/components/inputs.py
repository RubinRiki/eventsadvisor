# ui/components/inputs.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QComboBox, QPushButton


class SearchBar(QWidget):
    def __init__(self, placeholder="חיפוש...", parent=None):
        super().__init__(parent)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self.q = QLineEdit(self)
        self.q.setPlaceholderText(placeholder)
        self.city = QComboBox(self)
        self.city.addItems(["כל הערים", "ירושלים", "ת״א", "חיפה"])

        self.btn = QPushButton("חפש")
        self.btn.setObjectName("Primary")

        lay.addWidget(self.q, 1)
        lay.addWidget(self.city)
        lay.addWidget(self.btn)
