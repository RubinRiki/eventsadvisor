# client/app_shell.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt
import os

from .views.search_view import SearchView
from .views.details_view import DetailsView

try:
    from .views.consult_view import ConsultView
except Exception:
    ConsultView = None
try:
    from .views.charts_view import ChartsView
except Exception:
    ChartsView = None
try:
    from .views.profile_view import ProfileView
except Exception:
    ProfileView = None
try:
    from .views.login_view import LoginView
except Exception:
    LoginView = None


class AppShell(QMainWindow):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EventHub")
        self.resize(1200, 760)

        # ---- root ----
        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- Sidebar ----
        self.sidebar = QWidget(); self.sidebar.setObjectName("Sidebar")
        side = QVBoxLayout(self.sidebar); side.setContentsMargins(8, 12, 8, 12); side.setSpacing(6)

        self.btn_search  = QPushButton("חיפוש");       self.btn_search.setObjectName("SideItem")
        self.btn_profile = QPushButton("פרופיל");      self.btn_profile.setObjectName("SideItem")
        self.btn_consult = QPushButton("התייעצות");    self.btn_consult.setObjectName("SideItem")
        self.btn_charts  = QPushButton("סטטיסטיקות");  self.btn_charts.setObjectName("SideItem")
        self.btn_login   = QPushButton("התחברות");     self.btn_login.setObjectName("SideItem")

        spacer = QWidget(); spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        side.addWidget(self.btn_search)
        if ProfileView: side.addWidget(self.btn_profile)
        if ConsultView: side.addWidget(self.btn_consult)
        if ChartsView:  side.addWidget(self.btn_charts)
        if LoginView:   side.addWidget(self.btn_login)
        side.addWidget(spacer)

        # ---- Pages ----
        self.stack = QStackedWidget()
        self.search_view  = SearchView(self)
        self.details_view = DetailsView(self)
        self.stack.addWidget(self.search_view)   # index 0
        self.stack.addWidget(self.details_view)  # index 1

        if ProfileView:
            self.profile_view = ProfileView(self)      # טעינה עצלה דרך activate()
            self.stack.addWidget(self.profile_view)
        if ConsultView:
            self.consult_view = ConsultView(self); self.stack.addWidget(self.consult_view)
        if ChartsView:
            self.charts_view = ChartsView(self);   self.stack.addWidget(self.charts_view)
        if LoginView:
            self.login_view = LoginView(self);     self.stack.addWidget(self.login_view)
            # אות מה-LoginView: יכול לשלוח טוקן או בלי פרמטרים; נעדכן מצב התחברות
            try:
                # אם הסיגנל שולח את הטוקן כ- str
                self.login_view.loggedIn.connect(lambda token=None: self._on_logged_in(token))
            except Exception:
                pass

        layout.addWidget(self.sidebar, 0, Qt.AlignLeft)
        layout.addWidget(self.stack, 1)

        # ---- Wiring ----
        self.btn_search.clicked.connect(lambda: self._nav_to(self._index_of(SearchView), self.btn_search))
        if ProfileView:
            self.btn_profile.clicked.connect(self._go_profile)
        if ConsultView:
            self.btn_consult.clicked.connect(lambda: self._nav_to(self._index_of(ConsultView), self.btn_consult))
        if ChartsView:
            self.btn_charts.clicked.connect(lambda: self._nav_to(self._index_of(ChartsView), self.btn_charts))
        if LoginView:
            self.btn_login.clicked.connect(self._go_login)

        # פתיחת פרטי אירוע ממסך החיפוש
        self.search_view.openDetails.connect(self.navigate_to_event)

        # ---- Auth state on startup ----
        self._set_auth_state(self._is_authenticated(), initial=True)

    # -------- auth helpers --------
    def _is_authenticated(self) -> bool:
        tok = os.environ.get("AUTH_TOKEN")
        return bool(tok and tok.strip())

    def _on_logged_in(self, token: str | None = None):
        # אם ה-LoginView משדר לנו טוקן – נשמור אותו בסביבה לשימוש שאר המסכים
        if token and isinstance(token, str):
            os.environ["AUTH_TOKEN"] = token
        self._set_auth_state(True)

    def _set_auth_state(self, authenticated: bool, initial: bool = False):
        """מעדכן UI לפי מצב התחברות: מסתיר/מציג את לשונית 'התחברות', ומנווט נכון."""
        if LoginView:
            self.btn_login.setVisible(not authenticated)
        if ProfileView:
            self.btn_profile.setEnabled(authenticated)

        # כפתור נבחר (סטייל) + ניווט ראשוני
        if initial:
            if authenticated:
                self._nav_to(self._index_of(SearchView), self.btn_search)   # מתחילים בחיפוש
            else:
                self._go_login()
        else:
            # אחרי התחברות מוצלחת – ננווט למסך הראשי (חיפוש)
            if authenticated:
                self._nav_to(self._index_of(SearchView), self.btn_search)

    # -------- navigation helpers --------
    def _go_login(self):
        if LoginView:
            idx = self._index_of(LoginView)
            self._nav_to(idx, self.btn_login)
        else:
            self._nav_to(self._index_of(SearchView), self.btn_search)

    def _go_profile(self):
        # אם לא מחוברים — פותחים התחברות
        if not self._is_authenticated():
            self._go_login()
            return
        # מחוברים: נאקטב ואז ננווט לפרופיל
        if ProfileView:
            self._activate(ProfileView)
            self._nav_to(self._index_of(ProfileView), self.btn_profile)

    def _index_of(self, cls) -> int:
        for i in range(self.stack.count()):
            if isinstance(self.stack.widget(i), cls):
                return i
        return 0

    def _nav_to(self, index: int, btn: QPushButton | None):
        # איפוס מצב "current" לכל הכפתורים בסיידבר
        for b in (self.btn_search,
                  getattr(self, "btn_profile", None),
                  getattr(self, "btn_consult", None),
                  getattr(self, "btn_charts", None),
                  getattr(self, "btn_login", None)):
            if isinstance(b, QPushButton):
                b.setProperty("current", "false")
                b.style().unpolish(b); b.style().polish(b)
        if btn:
            btn.setProperty("current", "true")
            btn.style().unpolish(btn); btn.style().polish(btn)
        self.stack.setCurrentIndex(index)

    def _activate(self, cls):
        idx = self._index_of(cls)
        w = self.stack.widget(idx)
        if hasattr(w, "activate"):
            w.activate()

    def navigate_to_event(self, event_id: int):
        self._nav_to(self._index_of(DetailsView), None)
        self.details_view.load_event(event_id)
