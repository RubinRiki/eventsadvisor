import sys
import httpx
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox, QLabel
)

class EventsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EventAdvisor")
        self.resize(650, 420)

        layout = QVBoxLayout(self)

        self.info = QLabel("חפשי אירוע/אמן (אפשר להשאיר ריק להדגמה)")
        self.q = QLineEdit()
        self.q.setPlaceholderText("דוגמה: rock / Imagine Dragons / Tel Aviv")

        self.btnSearch = QPushButton("חיפוש אירועים")
        self.list = QListWidget()

        layout.addWidget(self.info)
        layout.addWidget(self.q)
        layout.addWidget(self.btnSearch)
        layout.addWidget(self.list)

        self.btnSearch.clicked.connect(self.on_search)

    def on_search(self):
        self.list.clear()
        q = self.q.text().strip()
        try:
            r = httpx.get("http://127.0.0.1:8000/events/search", params={"q": q}, timeout=12)
            r.raise_for_status()
            data = r.json()
            if not data:
                self.list.addItem("לא נמצאו אירועים")
                return
            for ev in data:
                name = ev.get("name") or "אירוע"
                date = ev.get("date") or "תאריך לא ידוע"
                venue = ev.get("venue") or "מקום לא ידוע"
                price = ev.get("price")
                price_txt = f" • {price}" if price else ""
                self.list.addItem(f"{name} — {date} @ {venue}{price_txt}")
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", str(e))

def main():
    app = QApplication(sys.argv)
    w = EventsApp()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
