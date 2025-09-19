# client/views/charts_view.py
# -*- coding: utf-8 -*-
from typing import List, Dict, Any, Optional
import os, requests

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
    QProgressBar, QSizePolicy
)
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QPen, QColor, QBrush, QFont
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis, QAreaSeries
)

from ..ui import Card, PageTitle, SectionTitle, Muted

# ===== Gateway base =====
GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

# ===== Local color tokens (בלי תלות ב-core/theme/palette) =====
C_TEXT        = "#E5E7EB"
C_BORDER      = "rgba(255,255,255,0.06)"
C_SURFACE     = "#0D1420"
C_ALT_BG      = "#0D1420"
C_TABLE_BG    = "#111826"
C_TABLE_HDR   = "#0F172A"
C_SELECTION   = "#22d3ee"

C_MUTED       = "rgba(255,255,255,0.65)"
C_PRIMARY     = "#4FC3F7"   # blue 300
C_SECONDARY   = "#FFD54F"   # amber 300
C_SUCCESS     = "#66BB6A"   # green 400
C_WARNING     = "#FFA726"   # orange 400
C_INFO        = "#29B6F6"   # light blue 400

class ChartsView(QWidget):
    """Dashboard: KPIs + Monthly Chart + Top Events table."""
    _dataReady = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 28, 16, 16)
        root.setSpacing(12)

        # Title + subtitle
        root.addWidget(PageTitle("נתונים חזותיים"))
        root.addWidget(Muted("סיכום מקורות: לפי חודש + ביצועי אירועים."))

        # ===== KPI tiles =====
        self.kpi_row = QHBoxLayout()
        self.kpi_row.setSpacing(12)

        self.kpi_events     = self._make_kpi("אירועים מפורסמים", C_INFO)
        self.kpi_confirmed  = self._make_kpi("אישורים", C_PRIMARY)
        self.kpi_waitlist   = self._make_kpi("וויט-ליסט", C_WARNING)
        self.kpi_util       = self._make_kpi("ניצולת ממוצעת", C_SUCCESS)

        for w in (self.kpi_events, self.kpi_confirmed, self.kpi_waitlist, self.kpi_util):
            self.kpi_row.addWidget(w)

        root.addLayout(self.kpi_row)

        # ===== Main content row =====
        row = QHBoxLayout(); row.setSpacing(12)

        # Left: monthly chart
        self.graph_card = Card()
        gl = QVBoxLayout(self.graph_card)
        gl.setContentsMargins(16, 16, 16, 16)
        gl.setSpacing(8)
        self.graph_title = SectionTitle("רישומים/אירועים לפי חודש")
        gl.addWidget(self.graph_title)
        self.chart_view = QChartView(QChart())
        self.chart_view.setRenderHint(self.chart_view.renderHints())
        gl.addWidget(self.chart_view, 1)
        row.addWidget(self.graph_card, 1)

        # Right: top events table
        self.table_card = Card()
        tl = QVBoxLayout(self.table_card)
        tl.setContentsMargins(16, 16, 16, 16)
        tl.setSpacing(8)
        tl.addWidget(SectionTitle("Top Events (Utilization)"))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["אירוע", "קיבולת", "מאושרים", "% ניצולת"])

        # Dark table styling – no P.*, רק קבועים מקומיים
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {C_TABLE_BG};
                color: {C_TEXT};
                gridline-color: {C_BORDER};
                alternate-background-color: {C_ALT_BG};
                selection-background-color: {C_SELECTION};
                selection-color: #111111;
                border: 1px solid {C_BORDER};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background: {C_TABLE_HDR};
                color: {C_TEXT};
                padding: 8px 10px;
                border: none;
                font-weight: 800;
            }}
        """)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        tl.addWidget(self.table, 1)
        row.addWidget(self.table_card, 1)

        # loader
        self._loading = QLabel("טוען…")
        self._loading.setAlignment(Qt.AlignCenter)
        self._loading.setObjectName("LoadingOverlay")

        root.addLayout(row, 1)
        root.addWidget(self._loading)
        self._show_loading(False)

        self._dataReady.connect(self._render)
        self.reload()  # first load

    # ---------- KPI helpers ----------
    def _make_kpi(self, title: str, color_hex: str) -> Card:
        """Create colored KPI card with a left accent strip + מקום לדלתא."""
        card = Card()
        v = QVBoxLayout(card)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(2)
        card.setStyleSheet(f"""
            QWidget {{
                background: {C_SURFACE};
                border: 1px solid {C_BORDER};
                border-radius: 12px;
            }}
            QWidget::before {{
                content: "";
                border-left: 6px solid {color_hex};
            }}
        """)
        caption = Muted(title)
        value = QLabel("—")
        value.setObjectName("KpiNumber")
        f = QFont(); f.setPointSizeF(20); f.setBold(True)
        value.setFont(f); value.setStyleSheet("color: white;")
        trend = QLabel("")  # דלתא חודשית (אפשר למלא בהמשך)
        trend.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        v.addWidget(caption); v.addWidget(value); v.addWidget(trend); v.addStretch(1)
        card._lbl_value = value
        card._lbl_trend = trend
        return card

    def _set_kpi(self, card: Card, value: str, delta: Optional[float] = None):
        card._lbl_value.setText(value)
        if delta is None:
            card._lbl_trend.setText("")
        else:
            arrow = "↑" if delta >= 0 else "↓"
            col   = C_SUCCESS if delta >= 0 else "#ef4444"
            card._lbl_trend.setText(f"<span style='color:{col}'>{arrow} {abs(delta):.1f}%</span> MoM")

    # ---------- data ----------
    def _headers(self) -> dict:
        h = {}
        tok = os.getenv("AUTH_TOKEN")
        if tok:
            h["Authorization"] = f"Bearer {tok}"
        return h

    def _fetch(self) -> dict:
        try:
            r = requests.get(f"{GATEWAY_BASE_URL}/analytics/summary",
                             headers=self._headers(), timeout=15)
            r.raise_for_status()
            return r.json() or {}
        except Exception as e:
            return {"error": str(e)}

    def reload(self):
        self._show_loading(True)
        self._dataReady.emit(self._fetch())

    # ---------- render ----------
    def _show_loading(self, on: bool):
        self._loading.setVisible(on)
        self.graph_card.setDisabled(on)
        self.table_card.setDisabled(on)

    def _render(self, data: dict):
        self._show_loading(False)
        try:
            if "error" in data:
                self._render_error(data["error"]); return

            totals   = data.get("totals") or {}
            by_month = data.get("by_month") or []
            top      = data.get("top_events") or []

            # הגנות טיפוסים
            if not isinstance(by_month, list): by_month = []
            if not isinstance(top, list): top = []

            # === KPIs ===
            total_events = int(totals.get("events_published") or 0)
            confirmed    = int(totals.get("registrations_confirmed") or 0)
            waitlist     = int(totals.get("registrations_waitlist") or 0)
            util_avg     = float(totals.get("capacity_utilization_pct") or 0.0)

            self._set_kpi(self.kpi_events,    f"{total_events:,}".replace(",", " "))
            self._set_kpi(self.kpi_confirmed, f"{confirmed:,}".replace(",", " "))
            self._set_kpi(self.kpi_waitlist,  f"{waitlist:,}".replace(",", " "))
            self._set_kpi(self.kpi_util,      f"{util_avg * 100:.1f}%")

            self._render_chart(by_month)
            self._render_table(top)

        except Exception as e:
            import traceback; traceback.print_exc()
            self._render_error(str(e))

    # ----- chart -----
    def _render_chart(self, by_month):
        points = sorted(by_month, key=lambda p: str(p.get("month","0000-00")))[:]
        labels = [str(p.get("month","")) for p in points]
        def nice(m): return (m[5:7] + "/" + m[2:4]) if len(m) >= 7 else m
        xlabels = [nice(m) for m in labels]

        def _to_int(x): 
            try: return int(x or 0)
            except: return 0

        regs = [_to_int(p.get("registrations")) for p in points]
        evts = [_to_int(p.get("created_events") or p.get("events")) for p in points]

        show_regs = any(v > 0 for v in regs)
        show_evts = any(v > 0 for v in evts)

        chart = QChart()
        ymax = 1

        if show_regs:
            s1 = QLineSeries(); s1.setName("Registrations")
            for i, y in enumerate(regs, start=1):
                s1.append(i, y); ymax = max(ymax, y)
            s1.setPen(QPen(QColor(C_PRIMARY), 2)); s1.setPointsVisible(True)
            chart.addSeries(s1)

        if show_evts:
            s2 = QLineSeries(); s2.setName("Created Events")
            for i, y in enumerate(evts, start=1):
                s2.append(i, y); ymax = max(ymax, y)
            s2.setPen(QPen(QColor(C_SECONDARY), 2)); s2.setPointsVisible(True)
            chart.addSeries(s2)

        axX = QCategoryAxis()
        if xlabels:
            for i, lab in enumerate(xlabels, start=1): axX.append(lab, i)
        else:
            axX.append("", 1)
        axX.setLabelsAngle(-35); axX.setGridLineVisible(True)

        axY = QValueAxis(); axY.setRange(0, ymax); axY.setTickCount(6)

        if chart.series():
            for s in chart.series(): chart.setAxisX(axX, s); chart.setAxisY(axY, s)
            chart.legend().setVisible(len(chart.series()) > 1)
            chart.setTitle("רישומים ואירועים לפי חודש")
        else:
            # סדרה דמה + כותרת ידידותית
            dummy = QLineSeries(); dummy.append(1, 0); dummy.append(2, 0)
            dummy.setPen(QPen(QColor(0,0,0,0), 0))
            chart.addSeries(dummy); chart.setAxisX(axX, dummy); chart.setAxisY(axY, dummy)
            chart.legend().setVisible(False)
            chart.setTitle("אין נתונים להצגה בטווח הנוכחי")

        self.chart_view.setChart(chart)

    def _render_table(self, top: List[Dict[str, Any]]):
        # normalize -> keep capacity > 0, calc utilization if missing
        rows: List[Dict[str, Any]] = []
        for ev in top:
            cap = int(ev.get("capacity") or 0)
            conf = int(ev.get("confirmed") or 0)
            if cap <= 0:
                continue
            util = ev.get("utilization_pct")
            if util is None:
                util = (conf / cap) * 100 if cap else 0.0
            else:
                util = float(util)
                # אם מגיע כשבר (0..1) – נעלה סקייל ל-אחוזים
                if util <= 1.0:
                    util *= 100.0

            rows.append({
                "title": str(ev.get("title") or ""),
                "capacity": cap,
                "confirmed": conf,
                "util": float(util),
            })

        rows.sort(key=lambda r: r["util"], reverse=True)
        rows = rows[:12]

        self.table.setRowCount(len(rows))

        # headers bold + center
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        for i in range(self.table.columnCount()):
            it = self.table.horizontalHeaderItem(i)
            if it:
                f = it.font(); f.setBold(True); it.setFont(f)

        # heat color helper
        def heat_color(pct: float) -> QColor:
            pct = max(0, min(100, int(round(pct))))
            if pct < 50:
                return QColor(79, 195, 247, 60)    # כחול שקוף
            elif pct < 80:
                return QColor(255, 213, 79, 80)    # ענברי
            else:
                return QColor(102, 187, 106, 90)   # ירקרק

        for r, ev in enumerate(rows):
            # col 0: title
            self.table.setItem(r, 0, QTableWidgetItem(ev["title"]))

            # col 1: capacity
            cell_cap = QTableWidgetItem(f"{ev['capacity']:,}".replace(",", " "))
            cell_cap.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 1, cell_cap)

            # col 2: confirmed
            cell_con = QTableWidgetItem(f"{ev['confirmed']:,}".replace(",", " "))
            cell_con.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 2, cell_con)

            # col 3: utilization % with progress bar
            pct = max(0, min(100, int(round(ev["util"]))))
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(pct)
            bar.setTextVisible(True)
            bar.setFormat(f"{pct}%")
            bar.setAlignment(Qt.AlignCenter)
            bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            bar.setFixedHeight(18)
            bar.setStyleSheet("""
                QProgressBar {
                    background: #1f2937;
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 6px;
                    color: #E5E7EB;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #22d3ee, stop:1 #10b981);
                    border-radius: 6px;
                }
            """)
            self.table.setCellWidget(r, 3, bar)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def _render_error(self, msg: str):
        chart = QChart(); chart.setTitle("שגיאה בטעינת נתונים")
        self.chart_view.setChart(chart)
        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem("שגיאה"))
        self.table.setItem(0, 1, QTableWidgetItem(msg))
        self.table.setItem(0, 2, QTableWidgetItem(""))
        self.table.setItem(0, 3, QTableWidgetItem(""))
