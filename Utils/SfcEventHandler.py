from DataAccess.FixtureData import FixtureData
from DataAccess.TestData import TestData
from DataAccess.TestParser import TestParser
from Models.Fixture import Fixture
from Models.Test import Test
from PyQt5 import QtCore
from watchdog.events import FileSystemEventHandler
import logging


class SfcEventHandler(FileSystemEventHandler, QtCore.QThread):
    updated = QtCore.pyqtSignal(Test, Fixture)

    def __init__(self) -> None:
        super().__init__()
        QtCore.QThread.__init__(self)
        self._testParser = TestParser()
        self._testData = TestData()
        self._fixtureData = FixtureData()

    def on_created(self, event):
        try:
            test = self._testParser.parse(event.src_path)
            self._testData.add(test, addToGoogleSheets=False)
            fixture = self._fixtureData.find(test.fixtureIp)
            self.updated.emit(test, fixture)
        except Exception as e:
            logging.error(str(e))
