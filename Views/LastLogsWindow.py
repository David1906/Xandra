from abc import abstractmethod
from DataAccess.MainConfigData import MainConfigData
from DataAccess.TestData import TestData
from Models.Fixture import Test
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from Utils.PathHelper import PathHelper
from Views.ImageWidget import ImageWidget
from Views.LogButton import LogButton


class LastLogsWindow(QtWidgets.QWidget):
    PAGE_SIZES = [10, 25, 50, 100, 200]

    def __init__(self, fixtureIp: str, title: str = "", biggestSliceColor=Qt.green):
        super().__init__()

        self.fixtureIp = fixtureIp
        self._testData = TestData()
        self._mainConfigData = MainConfigData()
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
        self.table.setMaximumHeight(450)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.gridLayout.addWidget(self.table, 1, 0, alignment=QtCore.Qt.AlignCenter)

        self.label = QtWidgets.QLabel("No Data Found")
        self.label.setStyleSheet(
            "font-size: 36px; font-weight: bold; text-align: center; margin: 20px"
        )
        self.gridLayout.addWidget(self.label, 0, 0, alignment=QtCore.Qt.AlignCenter)

        footer = QtWidgets.QHBoxLayout()

        self.btnStart = QtWidgets.QPushButton("Refresh")
        self.btnStart.clicked.connect(self.on_btn_refresh_click)
        footer.addWidget(self.btnStart)

        self.cmbSize = QtWidgets.QComboBox()
        yieldCalcQty = self._mainConfigData.get_yield_calc_qty()
        idxSelected = False
        for sizeIdx in range(len(LastLogsWindow.PAGE_SIZES)):
            size = LastLogsWindow.PAGE_SIZES[sizeIdx]
            self.cmbSize.addItem(str(size))
            if not idxSelected and (size >= yieldCalcQty):
                self.cmbSize.setCurrentIndex(sizeIdx)
                idxSelected = True
            elif not idxSelected and size == LastLogsWindow.PAGE_SIZES[-1]:
                self.cmbSize.addItem(str(yieldCalcQty))
                self.cmbSize.setCurrentIndex(sizeIdx + 1)

        self.cmbSize.activated[str].connect(self.on_cmb_size_change)
        footer.addWidget(self.cmbSize)
        self.gridLayout.addLayout(footer, 2, 0, QtCore.Qt.AlignCenter)

        self.refresh(int(self.cmbSize.currentText()))

    def on_cmb_size_change(self, size):
        self.refresh(int(size))

    def on_btn_refresh_click(self):
        self.refresh(int(self.cmbSize.currentText()))

    def refresh(self, qty: int = 10):
        data = self.getTests(qty)
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
    def getTests(self, qty: int):
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
                    btn.setToolTip(item)
                    self.table.setCellWidget(row, column, btn)
                elif keys[column] == "traceability" or keys[column] == "countInYield":
                    if item == True:
                        img = ImageWidget(
                            PathHelper().join_root_path("/Static/check.png"), self.table
                        )
                        self.table.setCellWidget(row, column, img)
                else:
                    self.table.setItem(
                        row, column, QtWidgets.QTableWidgetItem(str(item))
                    )
        fullPathIdx = keys.index("fullPath")
        keys[fullPathIdx] = "Logfile"
        self.table.setHorizontalHeaderLabels(keys)

    def _extractKeys(self, tests: "list[Test]") -> "list[str]":
        keys = list(tests[0].__dict__.keys())
        for rmKey in ["isNull"]:
            if rmKey in keys:
                keys.remove(rmKey)
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
