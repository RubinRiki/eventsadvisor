# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Client — views/charts_view.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
Charts/Analytics view that shows a simple demo:
- Left: a line chart (QtCharts) with fixed sample data.
- Right: a table synchronized with the same data.
- Uses UI building blocks (Card, PageTitle, SectionTitle, Muted).

Notes:
- Imports are package-relative (from ..ui ...) so running with
  `python -m client.app` works without import errors.
- Feel free to replace the demo data with real analytics from the API.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import QPointF
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

# ✅ Bring the UI components from the client UI package
from ..ui import Card, PageTitle, SectionTitle, Muted


class ChartsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 28, 16, 16)
        root.setSpacing(12)

        # Title + subtitle
        root.addWidget(PageTitle("נתונים חזותיים"))
        root.addWidget(Muted("דמו עיצוב: גרף קו + טבלה מסונכרנת."))

        row = QHBoxLayout()
        row.setSpacing(12)

        # -----------------
        # Chart (left card)
        # -----------------
        graph_card = Card()
        gl = QVBoxLayout(graph_card)
        gl.setContentsMargins(16, 16, 16, 16)
        gl.setSpacing(8)
        gl.addWidget(SectionTitle("ביצועים (דמו)"))

        # Demo data
        series = QLineSeries()
        data = [(1, 12), (2, 15), (3, 8), (4, 18), (5, 14), (6, 20), (7, 16)]
        for x, y in data:
            series.append(QPointF(x, y))

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.axisX().setTitleText("יום")
        chart.axisY().setTitleText("ערך")
        chart.setTitle("גרף קו (דמו)")
        chart.legend().hide()

        # Explicit axes setup
        axX = QValueAxis()
        axX.setRange(1, 7)
        axX.setTickCount(7)

        axY = QValueAxis()
        axY.setRange(0, 22)

        chart.setAxisX(axX, series)
        chart.setAxisY(axY, series)

        chart_view = QChartView(chart)
        gl.addWidget(chart_view, 1)
        row.addWidget(graph_card, 1)

        # ------------------
        # Table (right card)
        # ------------------
        table_card = Card()
        tl = QVBoxLayout(table_card)
        tl.setContentsMargins(16, 16, 16, 16)
        tl.setSpacing(8)
        tl.addWidget(SectionTitle("טבלה"))

        table = QTableWidget(len(data), 2)
        table.setHorizontalHeaderLabels(["יום", "ערך"])
        table.setAlternatingRowColors(True)

        for r, (x, y) in enumerate(data):
            table.setItem(r, 0, QTableWidgetItem(str(x)))
            table.setItem(r, 1, QTableWidgetItem(str(y)))

        table.resizeColumnsToContents()
        tl.addWidget(table, 1)

        # Assemble row
        row.addWidget(table_card, 1)
        root.addLayout(row, 1)
