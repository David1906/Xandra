import random
import subprocess
import threading
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import time


class TempThread(QtCore.QThread):
    readed = pyqtSignal(float)

    def __init__(self, toolPath: str = "", bmcIp: str = "", interval: int = 3):
        super().__init__()
        self._toolPath = toolPath
        self._bmcIp = bmcIp
        self._isStarted = False
        self._interval = interval
        self._threadEvent = threading.Event()

    def run(self):
        lastTemp = 0.0
        while True:
            try:
                self._threadEvent.wait()
                currentTemp = self._read_temp()
                if currentTemp != lastTemp:
                    lastTemp = currentTemp
                    self.readed.emit(currentTemp)
                time.sleep(self._interval)
            except:
                pass

    def _read_temp(self) -> float:
        try:
            currentTemp = subprocess.getoutput(
                "sh %s/Nitro/nitro-bmc -i %s sensors list |grep DTS|awk '{print $9}'"
                % (self._toolPath, self._bmcIp)
            )
            return float(currentTemp) / 1000
        except:
            return 0.0

    def resume(self, toolPath: str = "", bmcIp: str = ""):
        self._toolPath = toolPath
        self._bmcIp = bmcIp
        self._threadEvent.set()
        self._isStarted = True

    def pause(self):
        self._threadEvent.clear()
        self._isStarted = False

    def is_started(self) -> bool:
        return self._isStarted
