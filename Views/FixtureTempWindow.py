from DataAccess.FixtureTempDAO import FixtureTempDAO
from datetime import datetime, timedelta
from Models.DTO.FixtureTempDTO import FixtureTempDTO
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from Utils.Translator import Translator
from Views.TempView import TempView

_ = Translator().gettext


class FixtureTempWindow(QtWidgets.QWidget):
    X_AXIS_MINUTES = [
        "1 Min",
        "10 Min",
        "20 Min",
        "30 Min",
        "1 Hour",
        "2 Hours",
        "1 Day",
    ]
    X_AXIS_MINUTES_DICT = {
        "1 Min": 1,
        "10 Min": 10,
        "20 Min": 20,
        "30 Min": 30,
        "1 Hour": 60,
        "2 Hours": 120,
        "1 Day": 3600,
    }
    BLUE_SCHEME = [
        QColor(87, 125, 134),
        QColor(86, 157, 170),
        QColor(135, 203, 185),
        QColor(185, 237, 221),
        QColor(185, 237, 192),
    ]

    def __init__(self, fixtureId: int, parent=None):
        super().__init__(parent)

        self._fixtureId = fixtureId
        self._fixtureTempDAO = FixtureTempDAO()
        self._currentSize = FixtureTempWindow.X_AXIS_MINUTES[0]
        self._has_axes = False

        self._init_ui()

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.refresh)
        self.restart(self.cmbSize.currentText())

    def _init_ui(self):
        self.setWindowTitle(_("Temperature - Fixture {0}").format(self._fixtureId))

        # ************* Chart *************
        self._chart = QChart()
        self._chart.setMargins(QtCore.QMargins(0, 0, 0, 0))
        self._chart.setTheme(QChart.ChartThemeDark)
        self._chart.legend().hide()
        self._chartView = QChartView(self._chart)

        # ************* Axes *************
        self._axisX = QDateTimeAxis()
        self._axisX.setTickCount(10)
        self._axisX.setTitleText(_("Time"))
        self._axisX.setFormat("hh:mm:ss")
        self._axisY = QValueAxis()
        self._axisY.setTitleText(_("Temperature °C"))
        self._axisY.setLabelFormat("%i")
        self._axisY.setTickCount(7)
        self._axisY.setMax(150.0)
        self._axisY.setMin(0.0)

        # ************* Buttons *************

        self.btnRefresh = QtWidgets.QPushButton(_("Refresh"))
        self.btnRefresh.clicked.connect(self.on_refresh)

        self.cmbSize = QtWidgets.QComboBox()
        for sizeIdx in range(len(FixtureTempWindow.X_AXIS_MINUTES)):
            self.cmbSize.addItem(str(FixtureTempWindow.X_AXIS_MINUTES[sizeIdx]))
        self.cmbSize.setCurrentIndex(0)
        self.cmbSize.activated[str].connect(self.restart)

        # ************* Layout *************
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.setRowStretch(0, 1)
        gridLayout.setRowStretch(1, 0)
        gridLayout.addWidget(self._chartView, 0, 0, 1, 2)
        gridLayout.addWidget(self.cmbSize, 1, 0)
        gridLayout.addWidget(self.btnRefresh, 1, 1)
        self.setLayout(gridLayout)

        self.setFixedWidth(700)
        self.setFixedHeight(350)

    def restart(self, size):
        self._update_current_size(size)
        self._timer.stop()
        self._timer.setInterval(self._calc_timer_interval())
        self._timer.start()
        self.refresh()

    def _calc_timer_interval(self) -> int:
        return 30 * 1000 if self._should_grup_by_minute() else 5 * 1000

    def _update_current_size(self, size: str):
        self._currentSize = FixtureTempWindow.X_AXIS_MINUTES_DICT[size]

    def on_refresh(self):
        self.restart(self.cmbSize.currentText())

    def refresh(self):
        timeSpanMinutes = self._currentSize
        timeDelta = timedelta(minutes=timeSpanMinutes)
        items = self._fixtureTempDAO.find_last(
            self._fixtureId,
            timeDelta,
            groupByMinute=self._should_grup_by_minute(),
        )
        self.updateUtilizationChart(items, timeDelta)

    def _should_grup_by_minute(self):
        return self._currentSize > FixtureTempWindow.X_AXIS_MINUTES_DICT["10 Min"]

    def updateUtilizationChart(
        self, items: "list[FixtureTempDTO]", timeDelta: timedelta
    ):
        self._chart.removeAllSeries()
        series = QLineSeries(self)
        seriesLimit = QLineSeries(self)

        for item in items:
            series.append(
                self._datetime_to_ms_from_epoc(item.timeStamp), item.temp or 0
            )

        if len(items) == 0:
            series.append(0, 0)
        self._set_chart_series(timeDelta, series, seriesLimit)

    def _set_chart_series(
        self, timeDelta: timedelta, series: QLineSeries, seriesLimit: QLineSeries
    ):
        self._chart.addSeries(seriesLimit)
        self._chart.addSeries(series)
        if not self._has_axes:
            self._chart.addAxis(self._axisX, Qt.AlignBottom)
            self._chart.addAxis(self._axisY, Qt.AlignLeft)
            self._has_axes = True
        now = datetime.today()
        self._axisX.setMin(now - timeDelta)
        self._axisX.setMax(now)
        series.attachAxis(self._axisX)
        series.attachAxis(self._axisY)

        seriesLimit.append(self._datetime_to_ms_from_epoc(now), TempView.TEMP_ERROR)
        seriesLimit.append(
            self._datetime_to_ms_from_epoc(now - timeDelta), TempView.TEMP_ERROR
        )
        seriesLimit.setColor(QColor("salmon"))
        seriesLimit.attachAxis(self._axisX)
        seriesLimit.attachAxis(self._axisY)

    def _datetime_to_ms_from_epoc(self, dateTime: datetime) -> float:
        momentInTime = QtCore.QDateTime()
        momentInTime.setDate(dateTime.date())
        momentInTime.setTime(dateTime.time())
        return momentInTime.toMSecsSinceEpoch()

    def closeEvent(self, event):
        self._timer.stop()
