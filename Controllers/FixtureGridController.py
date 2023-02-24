from DataAccess.DisabledFixturesData import DisabledFixturesData
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
        self._disabledFixturesData = DisabledFixturesData()
        self._fixtureData = FixtureData()
        self._sfcEventHandler = SfcEventHandler()
        self._sfcEventHandler.updated.connect(self.update)
        self._fileWatchdog = FileWatchdog(self._sfcEventHandler)
        atexit.register(lambda: self._fileWatchdog.stop())

    def update(self, test: Test, fixture: Fixture):
        self._disabledFixturesData.save(fixture)
        self.updated.emit(test, fixture)

    def getAllFixtures(self) -> "list[Fixture]":
        return self._fixtureData.findAll()

    def startWatchLogs(self):
        self._fileWatchdog.start()

    def stopWatchLogs(self):
        self._fileWatchdog.stop()
