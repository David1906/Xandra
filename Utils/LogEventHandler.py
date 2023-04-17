from DataAccess.TestParser import TestParser
from Models.Fixture import Test
from PyQt5 import QtCore
from watchdog.events import FileSystemEventHandler
import logging
import os


class LogEventHandler(FileSystemEventHandler, QtCore.QThread):
    test_add = QtCore.pyqtSignal(Test)

    def __init__(self) -> None:
        super().__init__()
        QtCore.QThread.__init__(self)
        self._testParser = TestParser()

    def on_created(self, event):
        try:
            if os.path.isfile(event.src_path):
                test = self._testParser.parse(event.src_path)
                self.test_add.emit(test)
        except Exception as e:
            logging.error(str(e))
