from Core.Enums.FixtureMode import FixtureMode
from DataAccess.FixtureDAO import FixtureDAO
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.TestDAO import TestDAO
from DataAccess.TestParser import TestParser
from Models.Fixture import Fixture
from Models.Test import Test
from PyQt5 import QtCore
from Utils.BaseEventHandler import BaseEventHandler
from Utils.FileWatchdog import FileWatchdog
from Utils.FixtureSocket import FixtureSocket
from Utils.Translator import Translator
import atexit
import logging
import os
import pathlib


class FixtureGridController(QtCore.QThread):
    config_change = QtCore.pyqtSignal(object)
    fixture_change = QtCore.pyqtSignal(Fixture)
    test_started = QtCore.pyqtSignal(str)
    test_finished = QtCore.pyqtSignal(str, str, str)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self._isWatching = False
        self._testDAO = TestDAO()
        self._fixtureDAO = FixtureDAO()
        self._mainConfigDAO = MainConfigDAO()
        self._testParser = TestParser()

        self._baseEventHandler = BaseEventHandler()
        self._baseEventHandler.modified.connect(
            lambda event: self.on_config_change(event)
        )
        self._configWatchdog = FileWatchdog(self._baseEventHandler, timeout=1)
        self._configWatchdog.start(MainConfigDAO.MAIN_CONFIG_JSON_PATH)
        atexit.register(lambda: self._configWatchdog.stop())

        self._fixtureDAO.reset_mode()

        self._socket = FixtureSocket()
        self._socket.test_started.connect(self.on_test_started)
        self._socket.test_finished.connect(self.on_test_finished)
        self._socket.start()

    def on_test_started(self, fixtureIp: str):
        self.test_started.emit(fixtureIp)

    def on_test_finished(
        self, fixtureIp: str, serialNumber: str = "", logFileName: str = ""
    ):
        self.test_finished.emit(fixtureIp, serialNumber, logFileName)

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

    def parse_test(self, logFileName) -> Test:
        try:
            logFullpath = f"{self._mainConfigDAO.get_logs_path()}/{logFileName}"
            if (
                os.path.isfile(logFullpath)
                and pathlib.Path(logFullpath).suffix in Test.ALLOWED_EXTENSIONS
            ):
                return self._testParser.parse(logFullpath)
        except Exception as e:
            logging.error(str(e))
