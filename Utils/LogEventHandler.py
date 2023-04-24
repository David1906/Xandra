from DataAccess.TestParser import TestParser
from Models.Fixture import Test
from PyQt5 import QtCore
from watchdog.events import FileSystemEventHandler
import logging
import os
import pathlib


class LogEventHandler(FileSystemEventHandler, QtCore.QThread):
    ALLOWED_EXTENSIONS = [".log"]
    test_add = QtCore.pyqtSignal(Test)

    def __init__(self) -> None:
        super().__init__()
        QtCore.QThread.__init__(self)
        self._testParser = TestParser()

    def on_created(self, event):
        try:
            if (
                os.path.isfile(event.src_path)
                and pathlib.Path(event.src_path).suffix in LogEventHandler.ALLOWED_EXTENSIONS
            ):
                test = self._testParser.parse(event.src_path)
                self.test_add.emit(test)
        except Exception as e:
            logging.error(str(e))
