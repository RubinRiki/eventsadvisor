import sys
import httpx
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox
)

class BookAdvisor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BookAdvisor")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        self.q = QLineEdit()
        self.q.setPlaceholderText("חפשי ספר/מחבר...")

        self.btnSearch = QPushButton("חיפוש")
        self.list = QListWidget()

        layout.addWidget(self.q)
        layout.addWidget(self.btnSearch)
        layout.addWidget(self.list)

        self.btnSearch.clicked.connect(self.on_search)

    def on_search(self):
        self.list.clear()
        q = self.q.text().strip()
        try:
            r = httpx.get("http://127.0.0.1:8000/books/search", params={"q": q}, timeout=10)
            r.raise_for_status()
            data = r.json()
            if not data:
                self.list.addItem("לא נמצאו תוצאות")
                return
            for b in data:
                self.list.addItem(f"{b['title']} — {b['author']} [{b['genre']}]")
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", str(e))

def main():
    app = QApplication(sys.argv)
    w = BookAdvisor()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
