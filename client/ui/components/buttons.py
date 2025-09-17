# ui/components/buttons.py
from PySide6.QtWidgets import QPushButton


class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("Primary")


class SecondaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("Secondary")


class GhostButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("Ghost")
