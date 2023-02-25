from PyQt5 import QtCore
from watchdog.events import FileSystemEventHandler
import logging


class BaseEventHandler(FileSystemEventHandler, QtCore.QThread):
    modified = QtCore.pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        QtCore.QThread.__init__(self)

    def on_modified(self, event):
        try:
            self.modified.emit(event)
        except Exception as e:
            logging.error(str(e))
