# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Client — app_shell.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
This module defines the main application shell (window) for the EventHub client.
It wires the sidebar navigation and a central QStackedWidget that hosts the views.

Key ideas:
- A **right-to-left** layout for Hebrew UI.
- A **sidebar** with navigation buttons (Search, Charts/Table, Consult).
- A **stack** with 4 pages: Search, Details, Charts, Consult.
- Details page has **no dedicated sidebar button** by design; when showing Details,
  the "Search" button stays highlighted to reflect the flow "Search → Details".
"""

from typing import Optional

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
)

# ✅ Use package-relative imports so running from project root with `python -m client.app` works
from .core.theme.style_manager import apply_styles
from .views.search_view import SearchView
from .views.details_view import DetailsView
from .views.charts_view import ChartsView
from .views.consult_view import ConsultView


# Indices for the stacked widget (avoid magic numbers)
INDEX_SEARCH = 0
INDEX_DETAILS = 1
INDEX_CHARTS = 2
INDEX_CONSULT = 3


class AppShell(QWidget):
    """Main application window with sidebar navigation and central content stack."""

    def __init__(self, app, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Apply a global style/theme to the entire app
        apply_styles(app)

        # Basic window setup
        self.setWindowTitle("EventAdvisor")
        self.resize(1200, 760)
        self.setLayoutDirection(Qt.RightToLeft)  # Hebrew-friendly UI

        # Root horizontal layout: [ Sidebar | Stack ]
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # -------------------------
        # Sidebar (navigation area)
        # -------------------------
        side = QWidget()
        side.setObjectName("Sidebar")
        sl = QVBoxLayout(side)
        sl.setContentsMargins(8, 8, 8, 8)
        sl.setSpacing(4)

        self.btn_search = QPushButton("חיפוש")
        self.btn_search.setObjectName("SideItem")
        self.btn_search.setProperty("current", "true")  # default selected

        self.btn_charts = QPushButton("גרפים/טבלה")
        self.btn_charts.setObjectName("SideItem")

        self.btn_consult = QPushButton("ייעוץ")
        self.btn_consult.setObjectName("SideItem")

        for b in (self.btn_search, self.btn_charts, self.btn_consult):
            sl.addWidget(b)
        sl.addStretch(1)

        root.addWidget(side, 0)

        # -------------------------
        # Center stack (pages)
        # -------------------------
        self.stack = QStackedWidget()

        # Views: Search, Details, Charts, Consult
        self.view_search = SearchView()
        self.view_details = DetailsView()
        self.view_charts = ChartsView()
        self.view_consult = ConsultView()

        for v in (
            self.view_search,
            self.view_details,
            self.view_charts,
            self.view_consult,
        ):
            self.stack.addWidget(v)

        root.addWidget(self.stack, 1)

        # -------------------------
        # Wiring navigation
        # -------------------------
        self.btn_search.clicked.connect(lambda: self.navigate(INDEX_SEARCH))
        self.btn_charts.clicked.connect(lambda: self.navigate(INDEX_CHARTS))
        self.btn_consult.clicked.connect(lambda: self.navigate(INDEX_CONSULT))

        # When a card is clicked in Search, open the Details page for that event
        # Assumes SearchView exposes a Signal[str] named `openDetails`
        self.view_search.openDetails.connect(self._open_details)

    @Slot(int)
    def navigate(self, idx: int) -> None:
        """Switch visible page and update sidebar highlight."""
        self.stack.setCurrentIndex(idx)

        # Details has no button; keep 'Search' highlighted when idx == INDEX_DETAILS
        buttons = [self.btn_search, self.btn_charts, self.btn_consult]
        for i, btn in enumerate(buttons):
            current = (
                "true"
                if (i == idx) or (idx == INDEX_DETAILS and i == INDEX_SEARCH)
                else "false"
            )
            btn.setProperty("current", current)
            # Re-apply style to reflect the 'current' property change
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    @Slot(str)
    def _open_details(self, event_id: str) -> None:
        """Open Details view with the given event_id (demo placeholder content for now)."""
        # Demo content — replace with real fetch/bind later
        self.view_details.set_event(
            title=f"אירוע {event_id}",
            meta="היכל התרבות • תל אביב · 15/10/2025 · החל מ-₪180",
            description="תיאור קצר של האירוע… (דמו)",
        )
        self.navigate(INDEX_DETAILS)
