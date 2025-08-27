import sys
from PySide6.QtWidgets import QApplication
from app_shell import AppShell

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AppShell(app)
    win.show()
    sys.exit(app.exec())
