from Core.Enums.FixtureStatus import FixtureStatus
from DataAccess.FixtureStatusLogDAO import FixtureStatusLogDAO
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.MaintenanceDAO import MaintenanceDAO
from DataAccess.TestDAO import TestDAO
from datetime import timedelta
from Models.Fixture import Test
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QBrush
from Utils.Translator import Translator

_ = Translator().gettext


class MaintenanceLogView(QtWidgets.QWidget):
    PAGE_SIZES = ["10", "25", "50", "100", "200"]
    BLUE_SCHEME = [
        QColor(87, 125, 134),
        QColor(86, 157, 170),
        QColor(135, 203, 185),
        QColor(185, 237, 221),
        QColor(185, 237, 192),
    ]

    def __init__(
        self,
        fixtureIp: str,
    ):
        super().__init__()

        self.fixtureIp = fixtureIp
        self._testDAO = TestDAO()
        self._mainConfigDAO = MainConfigDAO()
        self._fixtureStatusLogDAO = FixtureStatusLogDAO()
        self._maintenanceDAO = MaintenanceDAO()
        self.series = None
        self.utilizationSeries = None

        self.setWindowTitle(_("Maintenance - Fixture {0}").format(fixtureIp))

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        dateTiemeLayout = QtWidgets.QHBoxLayout()
        dateTiemeLayout.setContentsMargins(0, 10, 0, 30)
        dateTiemeLayout.addWidget(QtWidgets.QLabel(_("Start:")))
        self.datetimeStart = QtWidgets.QDateTimeEdit(self, calendarPopup=True)
        yesterday = QtCore.QDateTime.currentDateTime().addDays(-1)
        yesterday = yesterday.addSecs(-yesterday.time().second().real)
        self.datetimeStart.setDateTime(yesterday)
        self.datetimeStart.dateTimeChanged.connect(self.refresh)
        dateTiemeLayout.addWidget(self.datetimeStart)

        dateTiemeLayout.addWidget(QtWidgets.QLabel(_("End:")))
        self.datetimeEnd = QtWidgets.QDateTimeEdit(self, calendarPopup=True)
        self.datetimeEnd.setDateTime(yesterday.addDays(1))
        self.datetimeEnd.dateTimeChanged.connect(self.refresh)
        dateTiemeLayout.addWidget(self.datetimeEnd)
        self.gridLayout.addLayout(dateTiemeLayout, 0, 0, 1, 2, QtCore.Qt.AlignCenter)

        self.utilizationChart = QChart()
        self.utilizationChart.setMargins(QtCore.QMargins(0, 0, 0, 0))
        self.utilizationChart.setTitle(_("Fixture Status Time"))
        self.utilizationChart.setAnimationOptions(QChart.SeriesAnimations)
        self.utilizationChart.setTheme(QChart.ChartThemeDark)
        chartView = QChartView(self.utilizationChart)
        self.gridLayout.addWidget(chartView, 1, 0)

        self.table = QtWidgets.QTableWidget()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.gridLayout.addWidget(self.table, 1, 1)

        self.label = QtWidgets.QLabel(_("No Data Found"))
        self.label.setStyleSheet(
            "font-size: 36px; font-weight: bold; text-align: center; margin: 20px"
        )
        self.gridLayout.addWidget(self.label, 1, 1, alignment=QtCore.Qt.AlignCenter)

        footer = QtWidgets.QHBoxLayout()

        self.btnStart = QtWidgets.QPushButton(_("Refresh"))
        self.btnStart.clicked.connect(self.on_btn_refresh_click)
        footer.addWidget(self.btnStart)

        self.cmbSize = QtWidgets.QComboBox()
        self.cmbSize.addItems(MaintenanceLogView.PAGE_SIZES)
        self.cmbSize.setCurrentIndex(3)

        self.cmbSize.activated[str].connect(self.on_cmb_size_change)
        footer.addWidget(self.cmbSize)
        footer.setContentsMargins(0, 30, 0, 10)
        self.gridLayout.addLayout(footer, 3, 0, 1, 2, QtCore.Qt.AlignCenter)

        self.refresh()

    def on_cmb_size_change(self, size):
        self.refresh()

    def on_btn_refresh_click(self):
        self.refresh()

    def refresh(self, qty: int = 10):
        qty = int(self.cmbSize.currentText())
        data = self._maintenanceDAO.find(
            self.fixtureIp,
            self.datetimeStart.dateTime().toPyDateTime(),
            self.datetimeEnd.dateTime().toPyDateTime(),
            qty,
        )
        hasData = len(data) > 0

        # self.table.setVisible(hasData)
        self.label.setVisible(not hasData)

        self.updateUtilizationChart()
        self.updateTable(data)

    def updateTable(self, logs: "list[Test]"):
        self.table.clear()
        row_count = len(logs)
        self.table.setRowCount(row_count)
        if len(logs) <= 0:
            return
        keys = self._extractKeys(logs)
        self.table.setColumnCount(len(keys))
        for row in range(row_count):
            for column in range(len(keys)):
                item = logs[row].__dict__[keys[column]]
                if item == None:
                    continue
                else:
                    self.table.setItem(
                        row, column, QtWidgets.QTableWidgetItem(str(item))
                    )
        self.table.setHorizontalHeaderLabels([_(key).capitalize() for key in keys])

    def _extractKeys(self, tests: "list[Test]") -> "list[str]":
        keys = list(tests[0].__dict__.keys())
        for rmKey in ["isNull", "_isNull", "fixtureId", "testId", "fixtureIp", "id"]:
            if rmKey in keys:
                keys.remove(rmKey)
        return keys

    def updateUtilizationChart(self):
        if self.utilizationSeries != None:
            self.utilizationChart.removeSeries(self.utilizationSeries)

        self.utilizationSeries = QPieSeries()
        logs = self._fixtureStatusLogDAO.find(
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
                _(FixtureStatus(log.status).description), log.seconds
            )

        my_slice = self.utilizationSeries.slices()[biggestSliceIdx]
        my_slice.setExploded(True)
        my_slice.setLabelVisible(True)
        my_slice.setPen(QPen(Qt.white, 2))

        i = 0
        for slice in self.utilizationSeries.slices():
            slice.setBrush(QBrush(MaintenanceLogView.BLUE_SCHEME[i]))
            txt = f"{slice.label()} - {str(timedelta(seconds=slice.value()))} - {100 * slice.percentage() :.2f}%"
            slice.setLabel(txt)
            slice.setLabelVisible(True)
            i += 1

        self.utilizationSeries.setHoleSize(0.5)
        self.utilizationChart.addSeries(self.utilizationSeries)
