from DataAccess.FixtureTempDAO import FixtureTempDAO
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import subprocess
import threading
import time


class TempThread(QtCore.QThread):
    readed = pyqtSignal(float)
    unavailable = pyqtSignal()

    def __init__(
        self,
        toolPath: str = "",
        bmcIp: str = "",
        interval: float = 1.5,
        fixtureId: int = 0,
    ):
        super().__init__()
        self._toolPath = toolPath
        self._bmcIp = bmcIp
        self._fixtureId = fixtureId
        self._isStarted = False
        self._interval = interval
        self._threadEvent = threading.Event()
        self._lastTemp = 0.0
        self._fixtureTempDAO = FixtureTempDAO()

    def run(self):
        while True:
            temp = None
            try:
                self._threadEvent.wait()
                temp = self._read_temp()
                self._fixtureTempDAO.add(self._fixtureId, temp)
            except Exception as e:
                temp = None
                print(f"TempThread error: {self._bmcIp}" + str(e))
            finally:
                self._emit_update_on_change(temp)
                time.sleep(self._interval)

    def _emit_update_on_change(self, temp: float):
        if temp != self._lastTemp:
            if temp == None:
                self.unavailable.emit()
            else:
                self.readed.emit(temp)
            self._lastTemp = temp

    def _read_temp(self) -> float:
        try:
            temp = subprocess.getoutput(
                "timeout 10s sh %s/Nitro/nitro-bmc -i %s sensors list |grep DTS|awk '{print $9}'"
                % (self._toolPath, self._bmcIp)
            )
            return float(temp) / 1000
        except:
            return None

    def resume(self, toolPath: str = "", bmcIp: str = "", fixtureId: int = 0):
        self._toolPath = toolPath
        self._bmcIp = bmcIp
        self._fixtureId = fixtureId
        self._threadEvent.set()
        self._isStarted = True

    def pause(self):
        self._threadEvent.clear()
        self._isStarted = False

    def is_started(self) -> bool:
        return self._isStarted
