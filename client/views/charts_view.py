# client/views/charts_view.py
# -*- coding: utf-8 -*-
from typing import List, Dict, Any, Optional
import os, requests

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel
)
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

from ..ui import Card, PageTitle, SectionTitle, Muted

GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://127.0.0.1:9000")

class ChartsView(QWidget):
    _dataReady = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 28, 16, 16)
        root.setSpacing(12)

        root.addWidget(PageTitle("נתונים חזותיים"))
        root.addWidget(Muted("סיכום מקורות: לפי חודש + טופ אירועים."))

        row = QHBoxLayout(); row.setSpacing(12)

        # Chart card
        self.graph_card = Card()
        gl = QVBoxLayout(self.graph_card); gl.setContentsMargins(16,16,16,16); gl.setSpacing(8)
        gl.addWidget(SectionTitle("רישומים לפי חודש"))
        self.chart_view = QChartView(QChart())
        gl.addWidget(self.chart_view, 1)
        row.addWidget(self.graph_card, 1)

        # Table card
        self.table_card = Card()
        tl = QVBoxLayout(self.table_card); tl.setContentsMargins(16,16,16,16); tl.setSpacing(8)
        tl.addWidget(SectionTitle("Top Events (Utilization)"))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["אירוע", "קיבולת", "מאושרים", "% ניצולת"])
        self.table.setAlternatingRowColors(True)
        tl.addWidget(self.table, 1)
        row.addWidget(self.table_card, 1)

        # Loading
        self._loading = QLabel("טוען…"); self._loading.setAlignment(Qt.AlignCenter); self._loading.setObjectName("LoadingOverlay")
        root.addLayout(row, 1)
        root.addWidget(self._loading); self._show_loading(False)

        self._dataReady.connect(self._render)
        self.reload()

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
        # אפשר פשוט לקרוא סינכרוני (זה קליל), אבל נוסיף “טוען…”
        self._show_loading(True)
        data = self._fetch()
        self._dataReady.emit(data)

    # ---------- render ----------
    def _show_loading(self, on: bool):
        self._loading.setVisible(on)
        self.graph_card.setDisabled(on); self.table_card.setDisabled(on)

    def _render(self, data: dict):
        self._show_loading(False)
        if "error" in data:
            self._render_error(data["error"])
            return

        # 1) גרף לפי חודש: ByMonth.points -> x=חודש כרונולוגי, y=registrations
        series = QLineSeries()
        points = data.get("by_month", [])
        # למיין לפי month "YYYY-MM"
        def _mkey(p): return p.get("month","0000-00")
        points = sorted(points, key=_mkey)
        for idx, p in enumerate(points, start=1):
            y = int(p.get("registrations", 0))
            series.append(QPointF(idx, y))

        chart = QChart()
        chart.addSeries(series)
        axX = QValueAxis(); axX.setRange(1, max(1, len(points))); axX.setTickCount(max(2, len(points)))
        axY = QValueAxis(); axY.setRange(0, max([int(p.get("registrations",0)) for p in points] + [1]))
        chart.setAxisX(axX, series); chart.setAxisY(axY, series)
        chart.legend().hide(); chart.setTitle("Registrations per Month")
        self.chart_view.setChart(chart)

        # 2) טבלת טופ אירועים לפי ניצולת
        top = data.get("top_events", [])
        self.table.setRowCount(len(top))
        for r, ev in enumerate(top):
            title = str(ev.get("title",""))
            cap   = int(ev.get("capacity", 0))
            conf  = int(ev.get("confirmed", 0))
            util  = float(ev.get("utilization_pct", 0.0))
            self.table.setItem(r, 0, QTableWidgetItem(title))
            self.table.setItem(r, 1, QTableWidgetItem(str(cap)))
            self.table.setItem(r, 2, QTableWidgetItem(str(conf)))
            self.table.setItem(r, 3, QTableWidgetItem(f"{util:.0f}%"))
        self.table.resizeColumnsToContents()

    def _render_error(self, msg: str):
        chart = QChart(); chart.setTitle("שגיאה בטעינת נתונים")
        self.chart_view.setChart(chart)
        self.table.setRowCount(1)
        self.table.setItem(0,0,QTableWidgetItem("שגיאה")); self.table.setItem(0,1,QTableWidgetItem(msg))
