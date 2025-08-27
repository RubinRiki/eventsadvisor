# app_shell.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PySide6.QtCore import Qt
from core.theme.style_manager import apply_styles
from views.search_view import SearchView
from views.details_view import DetailsView
from views.charts_view import ChartsView
from views.consult_view import ConsultView

class AppShell(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        apply_styles(app)  
        self.setWindowTitle("EventAdvisor")
        self.resize(1200, 760)
        self.setLayoutDirection(Qt.RightToLeft)

        root = QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Sidebar:
        side = QWidget(); side.setObjectName("Sidebar")
        sl = QVBoxLayout(side); sl.setContentsMargins(8,8,8,8); sl.setSpacing(4)
        self.btn_search = QPushButton("חיפוש"); self.btn_search.setObjectName("SideItem"); self.btn_search.setProperty("current","true")
        # self.btn_details = QPushButton("פרטים")  # לא צריך יותר כפתור פרטים!
        self.btn_charts = QPushButton("גרפים/טבלה"); self.btn_charts.setObjectName("SideItem")
        self.btn_consult = QPushButton("ייעוץ"); self.btn_consult.setObjectName("SideItem")
        for b in (self.btn_search, self.btn_charts, self.btn_consult): sl.addWidget(b)
        sl.addStretch(1)
        root.addWidget(side, 0)

        # Center stack:
        self.stack = QStackedWidget()
        self.view_search  = SearchView()
        self.view_details = DetailsView()
        self.view_charts  = ChartsView()
        self.view_consult = ConsultView()
        for v in (self.view_search, self.view_details, self.view_charts, self.view_consult):
            self.stack.addWidget(v)
        root.addWidget(self.stack, 1)

        # ניווט
        self.btn_search.clicked.connect(lambda: self.navigate(0))
        self.btn_charts.clicked.connect(lambda: self.navigate(2))
        self.btn_consult.clicked.connect(lambda: self.navigate(3))

        # מעבר מ-Search ל-Details בלחיצה על כרטיס
        self.view_search.openDetails.connect(self._open_details)

    def navigate(self, idx: int):
        self.stack.setCurrentIndex(idx)
        buttons = [self.btn_search, self.btn_charts, self.btn_consult]
        for i, btn in enumerate(buttons):
            btn.setProperty("current","true" if i==idx or (idx==1 and i==0) else "false")
            btn.style().unpolish(btn); btn.style().polish(btn)

    def _open_details(self, event_id: str):
    # דמו: הצגת נתוני placeholder
        self.view_details.set_event(
            title=f"אירוע {event_id}",
            meta="היכל התרבות • תל אביב · 15/10/2025 · החל מ-₪180",
            description="תיאור קצר של האירוע… (דמו)"
        )
        self.navigate(1)
