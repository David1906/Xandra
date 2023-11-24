import os
from DataAccess.FixtureTempDAO import FixtureTempDAO
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import subprocess
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
        self._lastTemp = 0.0
        self._fixtureTempDAO = FixtureTempDAO()

    def run(self):
        while True:
            temp = None
            try:
                if self._isStarted:
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
                "timeout 10s sh %s/Nitro/1.0.353.0/nitro-bmc -i %s sensors list |grep DTS|awk '{print $9}'"
                % (self._toolPath, self._bmcIp)
            )
            return float(temp) / 1000
        except:
            return None

    def _get_nitro_bmc_path(self):
        path1 = "%s/Nitro/1.0.353.0/nitro-bmc" % (self._toolPath)
        if os.path.isfile(path1):
            return path1
        return "%s/Nitro/nitro-bmc" % (self._toolPath)

    def resume(self, toolPath: str = "", bmcIp: str = "", fixtureId: int = 0):
        self._toolPath = toolPath
        self._bmcIp = bmcIp
        self._fixtureId = fixtureId
        self._isStarted = True

    def pause(self):
        self._isStarted = False

    def is_started(self) -> bool:
        return self._isStarted
