from Core.Enums.FixtureMode import FixtureMode
from DataAccess.FixtureDAO import FixtureDAO
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.TestDAO import TestDAO
from Models.Fixture import Fixture
from Models.FixtureConfig import FixtureConfig
from PyQt5 import QtCore
from Models.Test import Test
from Utils.BaseEventHandler import BaseEventHandler
from Utils.FileWatchdog import FileWatchdog
from Utils.FixtureSocket import FixtureSocket
from Utils.LogEventHandler import LogEventHandler
import atexit

from Utils.Translator import Translator


class FixtureGridController(QtCore.QThread):
    config_change = QtCore.pyqtSignal(object)
    fixture_change = QtCore.pyqtSignal(Fixture)
    test_add = QtCore.pyqtSignal(Test)
    testing_status_changed = QtCore.pyqtSignal(str, bool)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self._isWatching = False
        self._testDAO = TestDAO()
        self._fixtureDAO = FixtureDAO()
        self._mainConfigDAO = MainConfigDAO()

        self._sfcEventHandler = LogEventHandler()
        self._sfcEventHandler.test_add.connect(self.on_test_add)
        self._fileWatchdog = FileWatchdog(self._sfcEventHandler)
        atexit.register(lambda: self._fileWatchdog.stop())

        self._baseEventHandler = BaseEventHandler()
        self._baseEventHandler.modified.connect(
            lambda event: self.on_config_change(event)
        )
        self._configWatchdog = FileWatchdog(self._baseEventHandler, timeout=1)
        self._configWatchdog.start(MainConfigDAO.MAIN_CONFIG_JSON_PATH)
        atexit.register(lambda: self._configWatchdog.stop())

        self._fixtureDAO.reset_mode()

        self._socket = FixtureSocket()
        self._socket.testing_status_changed.connect(self.on_testing_status_change)
        self._socket.start()

    def on_test_add(self, test: Test):
        self.test_add.emit(test)

    def on_testing_status_change(self, fixtureIp: str, isTesting: bool):
        self.testing_status_changed.emit(fixtureIp, isTesting)

    def on_config_change(self, event):
        Translator().set_language_from_config()
        self.config_change.emit(event)
        for fixture in self.get_all_fixtures():
            self._fixtureDAO.create_or_update(fixture)
            self.fixture_change.emit(fixture)

    def get_all_fixtures(self) -> "list[Fixture]":
        fixtures = self._fixtureDAO.find_all()
        for fixture in fixtures:
            if fixture.mode == FixtureMode.UNKNOWN:
                fixture.mode = FixtureMode.ONLINE
                self._fixtureDAO.create_or_update(fixture)
        return fixtures

    def start_watch_logs(self):
        self._fileWatchdog.start(self._mainConfigDAO.get_logs_path())

    def stop_watch_logs(self):
        self._fileWatchdog.stop()
