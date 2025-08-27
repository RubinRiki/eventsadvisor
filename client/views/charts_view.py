# views/charts_view.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import QPointF
from ui.components.labels import PageTitle, SectionTitle, Muted
from ui.components.cards import Card

class ChartsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self); root.setContentsMargins(16,28,16,16); root.setSpacing(12)
        root.addWidget(PageTitle("נתונים חזותיים"))
        root.addWidget(Muted("דמו עיצוב: גרף קו + טבלה מסונכרנת."))

        row = QHBoxLayout(); row.setSpacing(12)

        # --- גרף ---
        graph_card = Card()
        gl = QVBoxLayout(graph_card); gl.setContentsMargins(16,16,16,16); gl.setSpacing(8)
        gl.addWidget(SectionTitle("ביצועים (דמו)"))

        series = QLineSeries()
        data = [(1,12),(2,15),(3,8),(4,18),(5,14),(6,20),(7,16)]
        for x,y in data:
            series.append(QPointF(x,y))

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.axisX().setTitleText("יום")
        chart.axisY().setTitleText("ערך")
        chart.setTitle("גרף קו (דמו)")
        chart.legend().hide()

        # צירים מדויקים
        axX = QValueAxis(); axX.setRange(1,7); axX.setTickCount(7)
        axY = QValueAxis(); axY.setRange(0,22)
        chart.setAxisX(axX, series); chart.setAxisY(axY, series)

        chart_view = QChartView(chart)
        gl.addWidget(chart_view, 1)
        row.addWidget(graph_card, 1)

        # --- טבלה ---
        table_card = Card()
        tl = QVBoxLayout(table_card); tl.setContentsMargins(16,16,16,16); tl.setSpacing(8)
        tl.addWidget(SectionTitle("טבלה"))
        table = QTableWidget(len(data), 2)
        table.setHorizontalHeaderLabels(["יום", "ערך"])
        table.setAlternatingRowColors(True)
        for r,(x,y) in enumerate(data):
            table.setItem(r,0,QTableWidgetItem(str(x)))
            table.setItem(r,1,QTableWidgetItem(str(y)))
        table.resizeColumnsToContents()
        tl.addWidget(table, 1)

        row.addWidget(table_card, 1)
        root.addLayout(row, 1)
