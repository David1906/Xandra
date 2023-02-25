from DataAccess.FixtureData import FixtureData
from DataAccess.MainConfigData import MainConfigData
from Models.Fixture import Fixture
from PyQt5 import QtCore
from Utils.BaseEventHandler import BaseEventHandler
from Utils.FileWatchdog import FileWatchdog
from Utils.LogEventHandler import LogEventHandler
import atexit


class FixtureGridController(QtCore.QThread):
    updated = QtCore.pyqtSignal(Fixture)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self._isWatching = False
        self._fixtureData = FixtureData()
        self._mainConfigData = MainConfigData()

        self._sfcEventHandler = LogEventHandler()
        self._sfcEventHandler.updated.connect(
            lambda fixture: self.updated.emit(fixture))
        self._fileWatchdog = FileWatchdog(self._sfcEventHandler)
        atexit.register(lambda: self._fileWatchdog.stop())

        self._baseEventHandler = BaseEventHandler()
        self._baseEventHandler.modified.connect(
            lambda event: self.on_config_change(event))
        self._configWatchdog = FileWatchdog(self._baseEventHandler)
        self._configWatchdog.start(MainConfigData.MAIN_CONFIG_JSON_PATH)
        atexit.register(lambda: self._configWatchdog.stop())

        self._fixtureData.refresh()

    def on_config_change(self, event):
        for fixture in self.get_all_fixtures():
            self._fixtureData.create_or_update(fixture)
            self.updated.emit(fixture)

    def get_all_fixtures(self) -> "list[Fixture]":
        return self._fixtureData.find_all()

    def start_watch_logs(self):
        self._fileWatchdog.start(self._mainConfigData.get_logs_path())

    def stop_watch_logs(self):
        self._fileWatchdog.stop()
