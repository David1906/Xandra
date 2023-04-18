from abc import abstractmethod
from Core.Enums.FixtureMode import FixtureMode
from Core.Enums.FixtureStatus import FixtureStatus
from DataAccess.FixtureStatusLogData import FixtureStatusLogData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.TestData import TestData
from datetime import datetime, timedelta
from Models.Fixture import Test
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QBrush
from Views.LogButton import LogButton
from Views.TestModeView import TestModeView


class LastLogsWindow(QtWidgets.QWidget):
    PAGE_SIZES = [10, 25, 50, 100, 200]
    BLUE_SCHEME = [
        QColor(87, 125, 134),
        QColor(86, 157, 170),
        QColor(135, 203, 185),
        QColor(185, 237, 221),
    ]

    def __init__(
        self,
        fixtureIp: str,
        title: str = "",
        biggestSliceColor=Qt.green,
        showRetest: bool = False,
    ):
        super().__init__()

        self.fixtureIp = fixtureIp
        self._testData = TestData()
        self._mainConfigData = MainConfigData()
        self._fixtureStatusLogData = FixtureStatusLogData()
        self.biggestSliceColor = biggestSliceColor
        self.series = None
        self.utilizationSeries = None
        self.showRetest = showRetest

        self.setWindowTitle(title)

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        self.chart = QChart()
        self.chart.setTitle("Yield")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        chartView = QChartView(self.chart)
        self.gridLayout.addWidget(chartView, 1, 0)

        dateTiemeLayout = QtWidgets.QHBoxLayout()
        dateTiemeLayout.addWidget(QtWidgets.QLabel("Start:"))
        self.datetimeStart = QtWidgets.QDateTimeEdit(self, calendarPopup=True)
        yesterday = QtCore.QDateTime.currentDateTime().addDays(-1)
        yesterday = yesterday.addSecs(-yesterday.time().second().real)
        self.datetimeStart.setDateTime(yesterday)
        self.datetimeStart.dateTimeChanged.connect(self.updateUtilizationChart)
        dateTiemeLayout.addWidget(self.datetimeStart)

        dateTiemeLayout.addWidget(QtWidgets.QLabel("End:"))
        self.datetimeEnd = QtWidgets.QDateTimeEdit(self, calendarPopup=True)
        self.datetimeEnd.setDateTime(yesterday.addDays(1))
        self.datetimeEnd.dateTimeChanged.connect(self.updateUtilizationChart)
        dateTiemeLayout.addWidget(self.datetimeEnd)
        self.gridLayout.addLayout(dateTiemeLayout, 0, 1, QtCore.Qt.AlignLeft)

        self.utilizationChart = QChart()
        self.utilizationChart.setTitle("Fixture Status Time")
        self.utilizationChart.setAnimationOptions(QChart.SeriesAnimations)
        self.utilizationChart.setTheme(QChart.ChartThemeDark)
        chartView = QChartView(self.utilizationChart)
        self.gridLayout.addWidget(chartView, 1, 1)

        self.table = QtWidgets.QTableWidget()
        self.table.setMaximumHeight(450)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.gridLayout.addWidget(
            self.table, 2, 0, 1, 2, alignment=QtCore.Qt.AlignCenter
        )

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

        self.chkShowRetest = QtWidgets.QCheckBox("Show Retest")
        self.chkShowRetest.setChecked(showRetest)
        self.chkShowRetest.stateChanged.connect(self.on_chk_show_retest)
        footer.addWidget(self.chkShowRetest)
        self.gridLayout.addLayout(footer, 3, 0, 1, 2, QtCore.Qt.AlignCenter)

        self.refresh(int(self.cmbSize.currentText()))

    def on_chk_show_retest(self):
        self.showRetest = self.chkShowRetest.isChecked()
        self.refresh(int(self.cmbSize.currentText()))

    def is_show_retest(self):
        return self.showRetest

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

        self.updateUtilizationChart()

        if not hasData:
            return
        self.updateTable(data)
        self.updateChart(data)

    @abstractmethod
    def getTests(self, qty: int):
        pass

    def updateTable(self, tests: "list[Test]"):
        self.table.clear()
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
                elif keys[column] == "mode":
                    self.table.setCellWidget(
                        row,
                        column,
                        TestModeView(FixtureMode(int(item))),
                    )
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
        greater = 0
        for key in keys:
            if greater < results[key]:
                greater = results[key]
                biggestSliceIdx = len(self.series)
            self.series.append(key, results[key])

        my_slice = self.series.slices()[biggestSliceIdx]
        my_slice.setExploded(True)
        my_slice.setLabelVisible(True)
        my_slice.setPen(QPen(Qt.white, 4))
        my_slice.setBrush(self.biggestSliceColor)

        for slice in self.series.slices():
            if slice.label() == "PASS":
                slice.setBrush(QBrush(QColor(16, 94, 98)))
            else:
                slice.setBrush(QBrush(QColor(181, 82, 92)))
            txt = f"{slice.label()} - {100 * slice.percentage() :.2f}%"
            slice.setLabel(txt)
            slice.setLabelVisible(True)

        self.chart.addSeries(self.series)

    def updateUtilizationChart(self):
        if self.utilizationSeries != None:
            self.utilizationChart.removeSeries(self.utilizationSeries)

        self.utilizationSeries = QPieSeries()
        logs = self._fixtureStatusLogData.find(
            self.fixtureIp,
            self.datetimeStart.dateTime().toPyDateTime(),
            self.datetimeEnd.dateTime().toPyDateTime(),
        )

        if len(logs) <= 0:
            return

        biggestSliceIdx = 0
        greater = 0
        for log in logs:
            if greater < log.seconds:
                greater = log.seconds
                biggestSliceIdx = len(self.utilizationSeries)
            self.utilizationSeries.append(
                FixtureStatus(log.status).description, log.seconds
            )

        my_slice = self.utilizationSeries.slices()[biggestSliceIdx]
        my_slice.setExploded(True)
        my_slice.setLabelVisible(True)
        my_slice.setPen(QPen(Qt.white, 4))
        my_slice.setBrush(self.biggestSliceColor)

        i = 0
        for slice in self.utilizationSeries.slices():
            slice.setBrush(QBrush(LastLogsWindow.BLUE_SCHEME[i]))
            txt = f"{slice.label()} - {str(timedelta(seconds=slice.value()))} - {100 * slice.percentage() :.2f}%"
            slice.setLabel(txt)
            slice.setLabelVisible(True)
            i += 1

        self.utilizationChart.addSeries(self.utilizationSeries)

    @abstractmethod
    def getResults(self, tests: "list[Test]"):
        pass

    @abstractmethod
    def processSlice(self, slice):
        pass
