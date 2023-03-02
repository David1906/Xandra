from abc import abstractmethod
from DataAccess.TestData import TestData
from Models.Test import Test
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from Views.LogButton import LogButton


class LastLogsWindow(QtWidgets.QWidget):
    def __init__(self, fixtureIp: str, title: str = "", biggestSliceColor=Qt.green):
        super().__init__()

        self.fixtureIp = fixtureIp
        self._testData = TestData()
        self.biggestSliceColor = biggestSliceColor
        self.series = None

        self.setWindowTitle(title)

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
        data = self.getTests()
        row_count = len(data)
        hasData = row_count > 0

        self.chart.setVisible(hasData)
        self.table.setVisible(hasData)
        self.label.setVisible(not hasData)

        if not hasData:
            return

        self.updateTable(data)
        self.updateChart(data)

    @abstractmethod
    def getTests(self):
        pass

    def updateTable(self, tests: "list[Test]"):
        row_count = len(tests)
        keys = self._extractKeys(tests)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(len(keys))
        for row in range(row_count):
            for column in range(len(keys)):
                item = tests[row].__dict__[keys[column]]
                if item == None:
                    continue
                if keys[column] == "status":
                    item = "PASS" if item == 1 else "FAILED"
                if keys[column] == "fullPath":
                    btn = LogButton(item)
                    self.table.setCellWidget(row, column, btn)
                else:
                    self.table.setItem(
                        row, column, QtWidgets.QTableWidgetItem(str(item))
                    )
        fullPathIdx = keys.index("fullPath")
        keys[fullPathIdx] = "Logfile"
        self.table.setHorizontalHeaderLabels(keys)

    def _extractKeys(self, tests: "list[Test]") -> "list[str]":
        keys = list(tests[0].__dict__.keys())
        keys.remove("countInYield")
        keys.remove("uploadToSFC")
        keys.remove("sfcError")
        return keys

    def updateChart(self, tests: "list[Test]"):
        if self.series != None:
            self.chart.removeSeries(self.series)

        self.series = QPieSeries()
        results = self.getResults(tests)

        keys = list(results.keys())
        biggestSliceIdx = 0
        greatter = 0
        for key in keys:
            if greatter < results[key]:
                greatter = results[key]
                biggestSliceIdx = len(self.series)
            self.series.append(key, results[key])

        my_slice = self.series.slices()[biggestSliceIdx]
        my_slice.setExploded(True)
        my_slice.setLabelVisible(True)
        my_slice.setPen(QPen(Qt.white, 4))
        my_slice.setBrush(self.biggestSliceColor)

        for slice in self.series.slices():
            if slice.label() == "PASS":
                slice.setBrush(Qt.green)
            else:
                slice.setBrush(Qt.red)

            txt = f"{slice.label()} - {100 * slice.percentage() :.2f}%"
            slice.setLabel(txt)
            slice.setLabelVisible(True)

        self.chart.addSeries(self.series)

    @abstractmethod
    def getResults(self, tests: "list[Test]"):
        pass

    @abstractmethod
    def processSlice(self, slice):
        pass
