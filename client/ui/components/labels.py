# ui/components/labels.py
from PySide6.QtWidgets import QLabel

class PageTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent); self.setStyleSheet("font-size:26px; font-weight:900; margin:0 0 6px 0;")

class SectionTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent); self.setStyleSheet("font-size:18px; font-weight:800; margin:0 0 6px 0;")

class Muted(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent); self.setStyleSheet("color:#8a94a6;")
