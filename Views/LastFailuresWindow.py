from PyQt5 import QtCore, QtWidgets
from DataAccess.XandraApiData import XandraApiData
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QIcon, QPen
from PyQt5.QtCore import Qt


class LastFailuresWindow(QtWidgets.QWidget):
    def __init__(self, fixtureIp: str):
        super().__init__()

        self.fixtureIp = fixtureIp
        self.xandraApiData = XandraApiData()
        self.series = None

        self.resize(950, 400)
        self.setWindowTitle(f"Last Failures - Fixture {fixtureIp}")

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        chartview = QChartView(self.chart)
        self.layout.addWidget(chartview)

        self.table = QtWidgets.QTableWidget()
        self.layout.addWidget(self.table)

        self.label = QtWidgets.QLabel("No Data Found")
        self.label.setStyleSheet(
            "font-size: 24px; font-weight: bold; text-align: center; margin: 20px"
        )
        self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)

        self.btnStart = QtWidgets.QPushButton("Refresh")
        self.btnStart.clicked.connect(self.refresh)
        self.layout.addWidget(self.btnStart, QtCore.Qt.AlignCenter)

        self.refresh()

    def refresh(self):
        data = self.xandraApiData.getLastFailures(self.fixtureIp)
        row_count = len(data)
        hasData = row_count > 0

        if hasData:
            column_count = len(data[0])
            self.table.setColumnCount(column_count)
            self.table.setRowCount(row_count)
            keys = list(data[0].keys())
            self.table.setHorizontalHeaderLabels(keys)
            for row in range(row_count):
                for column in range(column_count):
                    item = list(data[row].values())[column]
                    if keys[column] == "status":
                        item = "PASS" if item == 1 else "FAILED"
                    self.table.setItem(
                        row, column, QtWidgets.QTableWidgetItem(str(item))
                    )
            self.updateChart(data)

        self.chart.setVisible(hasData)
        self.table.setVisible(hasData)
        self.label.setVisible(not hasData)

    def updateChart(self, tests):
        if self.series != None:
            self.chart.removeSeries(self.series)

        self.series = QPieSeries()

        failures = {}
        for test in tests:
            key = test["stepLabel"]
            if key == "":
                key = "unknown"
            if key in failures:
                failures[key] = failures[key] + 1
            else:
                failures[key] = 1

        keys = list(failures.keys())
        biggestSeriesIdx = 0
        greatter = 0
        for key in keys:
            if greatter < failures[key]:
                greatter = failures[key]
                biggestSeriesIdx = len(self.series)
            self.series.append(key, failures[key])

        my_slice = self.series.slices()[biggestSeriesIdx]
        my_slice.setExploded(True)
        my_slice.setLabelVisible(True)
        my_slice.setPen(QPen(Qt.white, 4))
        my_slice.setBrush(Qt.green)

        for slice in self.series.slices():
            txt = f"{slice.label()} - {100 * slice.percentage() :.2f}%"
            slice.setLabel(txt)
            slice.setLabelVisible(True)

        self.chart.addSeries(self.series)
