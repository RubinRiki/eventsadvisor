from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QScrollArea
from PySide6.QtCore import Signal, Qt

from ui.components.inputs import SearchBar
from ui.components.cards import EventCard
from ui.components.labels import PageTitle, Muted

class SearchView(QWidget):
    searchRequested = Signal(str, dict)
    openDetails = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self); root.setContentsMargins(16,28,16,16); root.setSpacing(12)

        root.addWidget(PageTitle("חיפוש אירועים"))
        root.addWidget(Muted("מצאי/מצא במהירות לפי שם אמן, עיר או אולם."))

        self.searchbar = SearchBar("שם אמן / עיר / אולם")
        self.searchbar.btn.clicked.connect(self._emit_search)
        root.addWidget(self.searchbar)

        # Pills דמו
        pills_row = QHBoxLayout(); pills_row.setSpacing(6)
        for t in ["היום","מחר","סופ\"ש"]:
            lbl = QLabel(t); lbl.setObjectName("Pill")
            pills_row.addWidget(lbl)
        pills_row.addStretch(1)
        root.addLayout(pills_row)

        # Results grid בתוך Scroll
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); grid = QGridLayout(content); grid.setSpacing(12); grid.setContentsMargins(4,4,4,4)
        # 6 כרטיסים סטטיים לדמו נראות
        for i in range(6):
            card = EventCard(title=f"אירוע #{i+1}", venue="היכל התרבות • תל אביב", date="15/10", price="₪180")
            card.details_button.clicked.connect(lambda _, idx=i: self.openDetails.emit(f"demo{idx+1}"))
            grid.addWidget(card, i//3, i%3)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def _emit_search(self):
        q = self.searchbar.q.text().strip()
        filters = {"city": self.searchbar.city.currentText()}
        self.searchRequested.emit(q, filters)
