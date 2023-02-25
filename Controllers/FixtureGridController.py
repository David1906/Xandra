from DataAccess.FixtureData import FixtureData
from Models.Fixture import Fixture
from Models.Test import Test
from PyQt5 import QtCore
from Utils.FileWatchdog import FileWatchdog
from Utils.SfcEventHandler import SfcEventHandler
import atexit


class FixtureGridController(QtCore.QThread):
    updated = QtCore.pyqtSignal(Test, Fixture)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self._isWatching = False
        self._fixtureData = FixtureData()
        self._sfcEventHandler = SfcEventHandler()
        self._sfcEventHandler.updated.connect(self.update)
        self._fileWatchdog = FileWatchdog(self._sfcEventHandler)
        atexit.register(lambda: self._fileWatchdog.stop())

    def update(self, test: Test, fixture: Fixture):
        self.updated.emit(test, fixture)

    def get_all_fixtures(self) -> "list[Fixture]":
        return self._fixtureData.find_all()

    def start_watch_logs(self):
        self._fileWatchdog.start()

    def stop_watch_logs(self):
        self._fileWatchdog.stop()
