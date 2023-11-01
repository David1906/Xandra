import os
import random
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from threading import *
from threading import *
import time

from Utils.PathHelper import PathHelper


class TempView(QtWidgets.QWidget):
    def __init__(self, toolPath: str = "", bmcIp: str = "", parent=None):
        super(TempView, self).__init__(parent)
        self._toolPath = toolPath
        self._bmcIp = bmcIp
        self._init_ui()
        self._threadEvent = threading.Event()
        self._thread = Thread(target=self.read_temp_loop, args=(self._threadEvent,))
        self._thread.start()

    def _init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.lblTemp = QtWidgets.QLabel(self)
        self.lblTemp.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.lblTemp)

        self.lblIcon = QtWidgets.QLabel(self)
        self.lblIcon.hide()
        self.lblIcon.setAlignment(QtCore.Qt.AlignVCenter)
        pixmap = QPixmap(PathHelper().join_root_path(f"/Static/thermometer.png"))
        self.lblIcon.setPixmap(pixmap.scaled(16, 16))
        self.lblIcon.setContentsMargins(-10, 0, 0, 0)
        layout.addWidget(self.lblIcon, 0)

        layout.addStretch()
        self.setLayout(layout)

    def read_temp_loop(self, threadEvent: Event):
        lastTemp = 0.0
        while True:
            threadEvent.wait()
            currentTemp = self._read_temp()
            if currentTemp != lastTemp:
                self.lblTemp.setText(f"{currentTemp:+3.1f}°")
                self._update_color(currentTemp)
                lastTemp = currentTemp
            time.sleep(3)

    def _update_color(self, currentTemp: float):
        color = "gray"
        if currentTemp <= 50:
            color = "#4AA3BA"
        elif 50 < currentTemp and currentTemp < 70:
            color = "#5DAE8B"
        elif currentTemp >= 70:
            color = "#FF7676"
        self.lblTemp.setStyleSheet(
            f"background-color: {color};border-top-left-radius: 5px; border-bottom-left-radius: 5px;"
        )
        self.lblIcon.setStyleSheet(
            f"background-color: {color};border-top-right-radius: 5px; border-bottom-right-radius: 5px;"
        )

    def _read_temp(self) -> float:
        try:
            return float(
                os.popen(
                    "sh %s/Nitro/nitro-bmc -i %s sensors list |grep DTS|awk '{print $9}'"
                    % (self._toolPath, self._bmcIp)
                ).read()
            )
        except:
            return 0.0

    def start(self, toolPath: str = "", bmcIp: str = ""):
        self._toolPath = toolPath
        self._bmcIp = bmcIp
        self.lblTemp.setText("--.- °")
        self.lblIcon.show()
        self._threadEvent.set()

    def pause(self):
        self.lblTemp.setText("")
        self.lblIcon.hide()
        self._threadEvent.clear()

    def is_started(self) -> bool:
        self._threadEvent.is_set()
