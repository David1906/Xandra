from DataAccess.MainConfigData import MainConfigData
from watchdog.observers.polling import PollingObserver
import time


class FileWatchdog:
    def __init__(self, eventHandler):
        self.observer = PollingObserver()
        self.eventHandler = eventHandler
        self.mainConfigData = MainConfigData()

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.stop()
        self.observer.join()

    def start(self):
        path = self.mainConfigData.get_logs_path()
        print(f"Watching {path}...")
        self.observer.schedule(self.eventHandler, path, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
