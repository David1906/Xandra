import random
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
        interval: float = 2.5,
        fixtureId: int = 0,
        persist: bool = True,
    ):
        super().__init__()
        self._toolPath = toolPath
        self._bmcIp = bmcIp
        self._fixtureId = fixtureId
        self._isStarted = False
        self._persist = persist
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
                self._emit_update_on_change(temp)
                if self._persist:
                    self._fixtureTempDAO.add(self._fixtureId, temp or 0)
            except Exception as e:
                print(f"TempThread error: {self._bmcIp}" + str(e))
            finally:
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
        print(f"fixtureId {fixtureId}: TempThread resumed")
        self._toolPath = toolPath
        self._bmcIp = bmcIp
        self._fixtureId = fixtureId
        self._threadEvent.set()
        self._isStarted = True

    def pause(self):
        print(f"fixtureId {self._fixtureId}: TempThread resumed")
        self._threadEvent.clear()
        self._isStarted = False

    def is_started(self) -> bool:
        return self._isStarted
