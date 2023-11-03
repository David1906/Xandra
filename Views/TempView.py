from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from threading import *
from threading import *
from Utils.PathHelper import PathHelper
from Utils.TempThread import TempThread


class TempView(QtWidgets.QWidget):
    TEMP_OK = 40
    TEMP_ERROR = 76

    def __init__(self, toolPath: str = "", bmcIp: str = "", parent=None):
        super(TempView, self).__init__(parent)
        self._init_ui()
        self._tempThread = TempThread(toolPath, bmcIp)
        self._tempThread.readed.connect(self._on_temp_readed)
        self._tempThread.start()

    def _init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.lblTemp = QtWidgets.QLabel(self)
        self.lblTemp.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.lblTemp)

        self.lblIcon = QtWidgets.QLabel(self)
        self.lblIcon.setAlignment(QtCore.Qt.AlignVCenter)
        pixmap = QPixmap(PathHelper().join_root_path(f"/Static/thermometer.png"))
        self.lblIcon.setPixmap(pixmap.scaled(16, 16))
        self.lblIcon.setContentsMargins(-10, 0, 0, 0)
        layout.addWidget(self.lblIcon, 0)

        layout.addStretch()
        self.setLayout(layout)
        self.hide()

    def _on_temp_readed(self, temp: float):
        self.lblTemp.setText(f"{temp:+.1f}°")
        self._update_color(temp)

    def _update_color(self, currentTemp: float = 0):
        color = "#4AA3BA"
        if self.TEMP_OK < currentTemp and currentTemp < self.TEMP_ERROR:
            color = "#5DAE8B"
        elif currentTemp >= self.TEMP_ERROR:
            color = "#FF7676"
        self.lblTemp.setStyleSheet(
            f"background-color: {color};border-top-left-radius: 5px; border-bottom-left-radius: 5px;"
        )
        self.lblIcon.setStyleSheet(
            f"background-color: {color};border-top-right-radius: 5px; border-bottom-right-radius: 5px;"
        )

    def start(self, toolPath: str = "", bmcIp: str = ""):
        self.lblTemp.setText("--.- °")
        self._update_color(0)
        self.show()
        self._tempThread.resume(toolPath, bmcIp)

    def pause(self):
        self._tempThread.pause()
        self.hide()
        self.lblTemp.setText("")

    def is_started(self) -> bool:
        return self._tempThread.is_started()
