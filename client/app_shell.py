# client/app_shell.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt

# המסכים שלך
from .views.search_view import SearchView
from .views.details_view import DetailsView
# אופציונלי – אם קיימים אצלך
try:
    from .views.consult_view import ConsultView
except Exception:
    ConsultView = None
try:
    from .views.charts_view import ChartsView
except Exception:
    ChartsView = None


class AppShell(QMainWindow):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EventHub")
        self.resize(1200, 760)

        # ---- root container ----
        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- Sidebar (styled by QSS) ----
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(8, 12, 8, 12)
        side.setSpacing(6)

        self.btn_search  = QPushButton("חיפוש")
        self.btn_search.setObjectName("SideItem")
        self.btn_search.setProperty("current", "true")  # התחל מסומן

        self.btn_consult = QPushButton("התייעצות")
        self.btn_consult.setObjectName("SideItem")

        self.btn_charts  = QPushButton("סטטיסטיקות")
        self.btn_charts.setObjectName("SideItem")

        # ממלא חלל (שומר את הכפתורים למעלה)
        spacer = QWidget(); spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        side.addWidget(self.btn_search)
        if ConsultView: side.addWidget(self.btn_consult)
        if ChartsView:  side.addWidget(self.btn_charts)
        side.addWidget(spacer)

        # ---- Stacked pages ----
        self.stack = QStackedWidget()

        self.search_view  = SearchView(self)
        self.details_view = DetailsView(self)
        self.stack.addWidget(self.search_view)   # index 0
        self.stack.addWidget(self.details_view)  # index 1

        if ConsultView:
            self.consult_view = ConsultView(self); self.stack.addWidget(self.consult_view)
        if ChartsView:
            self.charts_view = ChartsView(self);   self.stack.addWidget(self.charts_view)

        # ---- Lay them out ----
        layout.addWidget(self.sidebar, 0, Qt.AlignLeft)
        layout.addWidget(self.stack, 1)

        # ---- Wiring ----
        self.btn_search.clicked.connect(lambda: self._nav_to(0, self.btn_search))
        if ConsultView:
            self.btn_consult.clicked.connect(lambda: self._nav_to(self._index_of(ConsultView), self.btn_consult))
        if ChartsView:
            self.btn_charts.clicked.connect(lambda: self._nav_to(self._index_of(ChartsView), self.btn_charts))

        # מעבר למסך פרטים בלחיצה על "פרטים" בכרטיס
        self.search_view.openDetails.connect(
            lambda eid: (self._nav_to(1, None), self.details_view.load_event(eid))
        )

        # התחל בחיפוש
        self.stack.setCurrentIndex(0)

    def _index_of(self, cls) -> int:
        # מאתר אינדקס לפי טיפוס הווידג'ט
        for i in range(self.stack.count()):
            if isinstance(self.stack.widget(i), cls):
                return i
        return 0

    def _nav_to(self, index: int, btn: QPushButton | None):
        # עדכון מצב "current" לסטיילינג
        for b in (self.btn_search, self.btn_consult, self.btn_charts):
            if isinstance(b, QPushButton):
                b.setProperty("current", "false")
                b.style().unpolish(b); b.style().polish(b)
        if btn:
            btn.setProperty("current", "true")
            btn.style().unpolish(btn); btn.style().polish(btn)
        self.stack.setCurrentIndex(index)
