from DataAccess.FixtureData import FixtureData
from DataAccess.TestData import TestData
from DataAccess.TestParser import TestParser
from Models.Fixture import Fixture
from PyQt5 import QtCore
from watchdog.events import FileSystemEventHandler
import logging


class LogEventHandler(FileSystemEventHandler, QtCore.QThread):
    updated = QtCore.pyqtSignal(Fixture)

    def __init__(self) -> None:
        super().__init__()
        QtCore.QThread.__init__(self)
        self._testParser = TestParser()
        self._testData = TestData()
        self._fixtureData = FixtureData()

    def on_created(self, event):
        try:
            test = self._testParser.parse(event.src_path)
            fixture = self._fixtureData.find(test.fixtureIp)
            fixture.configure(test)

            self._testData.add(test)
            self._fixtureData.create_or_update(fixture)

            if test.uploadToSFC:
                test.sfcError = not self._fixtureData.upload_pass_to_sfc(
                    test.serialNumber
                )

            fixture = self._fixtureData.find(test.fixtureIp)
            fixture.set_test(test)
            self.updated.emit(fixture)
        except Exception as e:
            logging.error(str(e))
