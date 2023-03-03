from DataAccess.FixtureData import FixtureData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.TestData import TestData
from Models.FixtureConfig import FixtureConfig
from PyQt5 import QtCore
from Models.Test import Test
from Utils.BaseEventHandler import BaseEventHandler
from Utils.FileWatchdog import FileWatchdog
from Utils.FixtureSocket import FixtureSocket
from Utils.LogEventHandler import LogEventHandler
import atexit


class FixtureGridController(QtCore.QThread):
    fixture_config_update = QtCore.pyqtSignal(FixtureConfig)
    test_add = QtCore.pyqtSignal(Test)
    testing_status_changed = QtCore.pyqtSignal(str, bool)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self._isWatching = False
        self._testData = TestData()
        self._fixtureData = FixtureData()
        self._mainConfigData = MainConfigData()

        self._sfcEventHandler = LogEventHandler()
        self._sfcEventHandler.test_add.connect(self.on_test_add)
        self._fileWatchdog = FileWatchdog(self._sfcEventHandler)
        atexit.register(lambda: self._fileWatchdog.stop())

        self._baseEventHandler = BaseEventHandler()
        self._baseEventHandler.modified.connect(
            lambda event: self.on_config_change(event)
        )
        self._configWatchdog = FileWatchdog(self._baseEventHandler)
        self._configWatchdog.start(MainConfigData.MAIN_CONFIG_JSON_PATH)
        atexit.register(lambda: self._configWatchdog.stop())

        self._fixtureData.refresh(resetFixture=True)

        self._socket = FixtureSocket()
        self._socket.testing_status_changed.connect(self.on_testing_status_change)
        self._socket.start()

    def on_test_add(self, test: Test):
        self.test_add.emit(test)

    def on_testing_status_change(self, fixtureIp: str, isTesting: bool):
        self.testing_status_changed.emit(fixtureIp, isTesting)

    def on_config_change(self, event):
        for fixture in self.get_all_fixtures():
            self._fixtureData.create_or_update(fixture)
            self.fixture_config_update.emit(fixture)

    def get_all_fixtures(self) -> "list[FixtureConfig]":
        return self._fixtureData.find_all()

    def start_watch_logs(self):
        self._fileWatchdog.start(self._mainConfigData.get_logs_path())

    def stop_watch_logs(self):
        self._fileWatchdog.stop()
