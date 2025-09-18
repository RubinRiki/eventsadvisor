# client/views/charts_view.py
# -*- coding: utf-8 -*-
from typing import List, Dict, Any
import os, requests

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel
)
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QPen, QColor, QBrush, QFont
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis
)

from ..ui import Card, PageTitle, SectionTitle, Muted

GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")


# ===== Utility colors (Azure-like) =====
C_PRIMARY   = "#4FC3F7"   # blue 300
C_SECONDARY = "#FFD54F"   # amber 300
C_SUCCESS   = "#66BB6A"   # green 400
C_WARNING   = "#FFA726"   # orange 400
C_INFO      = "#29B6F6"   # light blue 400
C_MUTED     = "rgba(255,255,255,0.65)"


class ChartsView(QWidget):
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
        self.graph_title = SectionTitle("רישומים לפי חודש")
        gl.addWidget(self.graph_title)
        self.chart_view = QChartView(QChart())
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
        # ==== Dark-table styling so it's NOT white ====
        self.table.setStyleSheet("""
            QTableWidget {
                background: #111826;                 /* תואם רקעים כהים */
                color: #E5E7EB;                      /* טקסט בהיר */
                gridline-color: rgba(255,255,255,0.08);
                alternate-background-color: #0D1420;
                selection-background-color: rgba(79,195,247,0.20);
                selection-color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 8px;
            }
            QHeaderView::section {
                background: #0F172A;
                color: #E5E7EB;
                padding: 6px 8px;
                border: none;
                border-bottom: 1px solid rgba(255,255,255,0.08);
                font-weight: 700;
            }
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
        self.reload()

    # ---------- KPI helpers ----------
    def _make_kpi(self, title: str, color_hex: str) -> Card:
        """Create colored KPI card with a left accent strip (Azure-like)."""
        card = Card()
        v = QVBoxLayout(card)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(2)
        # left accent using stylesheet on the card
        card.setStyleSheet(f"""
            QWidget {{
                background: #0D1420;
                border: 1px solid rgba(255,255,255,0.06);
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
        f = QFont(); f.setPointSizeF(18); f.setBold(True)
        value.setFont(f)
        value.setStyleSheet("color: white;")
        v.addWidget(caption)
        v.addWidget(value)
        v.addStretch(1)
        # keep a handle to value label
        card._lbl_value = value
        return card

    def _set_kpi(self, card: Card, value: str):
        card._lbl_value.setText(value)

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
                             headers=self._headers(), timeout=12)
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
        if "error" in data:
            self._render_error(data["error"])
            return

        totals = data.get("totals", {}) or {}
        by_month = data.get("by_month", []) or []
        top = data.get("top_events", []) or []

        # === KPIs ===
        total_events = int(totals.get("events_published") or 0)
        confirmed    = int(totals.get("registrations_confirmed") or 0)
        waitlist     = int(totals.get("registrations_waitlist") or 0)
        util_avg     = float(totals.get("capacity_utilization_pct") or 0.0)

        self._set_kpi(self.kpi_events,    f"{total_events:,}".replace(",", " "))
        self._set_kpi(self.kpi_confirmed, f"{confirmed:,}".replace(",", " "))
        self._set_kpi(self.kpi_waitlist,  f"{waitlist:,}".replace(",", " "))
        self._set_kpi(self.kpi_util,      f"{util_avg:.0f}%")

        # === Monthly chart (2 series + colors + month labels) ===
        self._render_chart(by_month)

        # === Top events table (dark + heat coloring) ===
        self._render_table(top)

    # ----- chart -----
    def _render_chart(self, by_month: List[Dict[str, Any]]):
        # sort & limit 12 months
        points = sorted(by_month, key=lambda p: str(p.get("month", "0000-00")))[-12:]
        labels = [str(p.get("month", "")) for p in points]  # YYYY-MM
        def nice(m: str) -> str:
            return (m[5:7] + "/" + m[2:4]) if len(m) >= 7 else m
        xlabels = [nice(m) for m in labels]

        regs = [int(p.get("registrations") or 0) for p in points]
        evts = [int(p.get("created_events") or p.get("events") or 0) for p in points]

        show_regs = any(v > 0 for v in regs)
        show_evts = any(v > 0 for v in evts)

        chart = QChart()
        ymax = 1

        if show_regs:
            s1 = QLineSeries(); s1.setName("Registrations")
            for i, y in enumerate(regs, start=1):
                s1.append(QPointF(i, y)); ymax = max(ymax, y)
            s1.setPen(QPen(QColor(C_PRIMARY), 2))
            s1.setPointsVisible(True)
            chart.addSeries(s1)

        # אם אין רישומים – נציג אירועים; אם יש – נציג גם וגם
        if show_evts and (not show_regs or True):
            s2 = QLineSeries(); s2.setName("Created Events")
            for i, y in enumerate(evts, start=1):
                s2.append(QPointF(i, y)); ymax = max(ymax, y)
            s2.setPen(QPen(QColor(C_SECONDARY), 2))
            s2.setPointsVisible(True)
            chart.addSeries(s2)

        axX = QCategoryAxis()
        for i, lab in enumerate(xlabels, start=1):
            axX.append(lab, i)
        axX.setLabelsAngle(-35)
        axX.setGridLineVisible(True)

        axY = QValueAxis()
        axY.setRange(0, ymax)
        axY.setTickCount(5)

        for s in chart.series():
            chart.setAxisX(axX, s); chart.setAxisY(axY, s)

        chart.legend().setVisible(len(chart.series()) > 1)
        chart.setTitle("Registrations per Month" if show_regs else "Events Created per Month")
        self.chart_view.setChart(chart)

    # ----- table -----
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
            rows.append({
                "title": str(ev.get("title") or ""),
                "capacity": cap,
                "confirmed": conf,
                "util": float(util),
            })
        rows.sort(key=lambda r: r["util"], reverse=True)
        rows = rows[:12]

        self.table.setRowCount(len(rows))

        # prettier headers
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        for i in range(self.table.columnCount()):
            it = self.table.horizontalHeaderItem(i)
            if it:
                f = it.font(); f.setBold(True); it.setFont(f)

        def heat_color(pct: float) -> QColor:
            # 0..100 -> color
            pct = max(0.0, min(100.0, pct))
            if pct < 50:
                return QColor(79, 195, 247, 60)    # blue-ish
            elif pct < 80:
                return QColor(255, 213, 79, 80)    # amber
            else:
                return QColor(102, 187, 106, 90)   # green

        for r, ev in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(ev["title"]))

            cell_cap = QTableWidgetItem(str(ev["capacity"]))
            cell_cap.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 1, cell_cap)

            cell_con = QTableWidgetItem(str(ev["confirmed"]))
            cell_con.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 2, cell_con)

            util_str = f'{ev["util"]:.0f}%'
            cell_utl = QTableWidgetItem(util_str)
            cell_utl.setTextAlignment(Qt.AlignCenter)
            cell_utl.setBackground(QBrush(heat_color(ev["util"])))
            cell_utl.setToolTip(
                f"Utilization = confirmed/capacity = {ev['confirmed']}/{ev['capacity']}"
            )
            self.table.setItem(r, 3, cell_utl)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def _render_error(self, msg: str):
        chart = QChart(); chart.setTitle("שגיאה בטעינת נתונים")
        self.chart_view.setChart(chart)
        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem("שגיאה"))
        self.table.setItem(0, 1, QTableWidgetItem(msg))
