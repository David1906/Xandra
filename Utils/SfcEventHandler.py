import logging
from watchdog.events import FileSystemEventHandler
from DataAccess.TestData import TestData


class SfcEventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.testData = TestData()

    def on_created(self, event):
        try:
            test = self.testData.parse(event.src_path)
            self.testData.add(test, addToGoogleSheets=False)
        except Exception as e:
            logging.error(str(e))
