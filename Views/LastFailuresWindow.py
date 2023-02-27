from DataAccess.TestData import TestData
from Models.Test import Test
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen

from Views.LogButton import LogButton


class LastFailuresWindow(QtWidgets.QWidget):
    def __init__(self, fixtureIp: str):
        super().__init__()

        self.fixtureIp = fixtureIp
        self._testData = TestData()
        self.series = None

        self.setWindowTitle(f"Last Failures - Fixture {fixtureIp}")

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        chartview = QChartView(self.chart)
        self.gridLayout.addWidget(chartview, 0, 0)

        self.table = QtWidgets.QTableWidget()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.gridLayout.addWidget(self.table, 1, 0, alignment=QtCore.Qt.AlignCenter)

        self.label = QtWidgets.QLabel("No Data Found")
        self.label.setStyleSheet(
            "font-size: 36px; font-weight: bold; text-align: center; margin: 20px"
        )
        self.gridLayout.addWidget(self.label, 0, 0, alignment=QtCore.Qt.AlignCenter)

        self.btnStart = QtWidgets.QPushButton("Refresh")
        self.btnStart.clicked.connect(self.refresh)
        self.gridLayout.addWidget(self.btnStart, 2, 0, QtCore.Qt.AlignCenter)
        self.refresh()

    def refresh(self):
        data = self._testData.find_last_failures(self.fixtureIp)
        row_count = len(data)
        hasData = row_count > 0

        self.chart.setVisible(hasData)
        self.table.setVisible(hasData)
        self.label.setVisible(not hasData)

        if not hasData:
            return

        self.updateTable(data)
        self.updateChart(data)

    def updateTable(self, tests: "list[Test]"):
        row_count = len(tests)
        column_count = len(tests[0].__dict__)
        self.table.setColumnCount(column_count)
        self.table.setRowCount(row_count)
        keys = list(tests[0].__dict__.keys())
        for column in range(column_count):
            if keys[column] == "fullPath":
                keys[column] = "Logfile"
        self.table.setHorizontalHeaderLabels(keys)
        for row in range(row_count):
            for column in range(column_count):
                item = list(tests[row].__dict__.values())[column]
                if item == None:
                    continue
                if keys[column] == "status":
                    item = "PASS" if item == 1 else "FAILED"
                if keys[column] == "Logfile":
                    btn = LogButton(item)
                    self.table.setCellWidget(row, column, btn)
                else:
                    self.table.setItem(
                        row, column, QtWidgets.QTableWidgetItem(str(item))
                    )

    def updateChart(self, tests: "list[Test]"):
        if self.series != None:
            self.chart.removeSeries(self.series)

        self.series = QPieSeries()

        failures = {}
        for test in tests:
            key = test.stepLabel
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
        my_slice.setBrush(Qt.red)

        for slice in self.series.slices():
            txt = f"{slice.label()} - {100 * slice.percentage() :.2f}%"
            slice.setLabel(txt)
            slice.setLabelVisible(True)

        self.chart.addSeries(self.series)
