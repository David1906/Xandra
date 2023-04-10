from watchdog.observers.polling import PollingObserver as Observer
import time


class FileWatchdog:
    def __init__(self, eventHandler):
        self._observer = Observer(2)
        self._eventHandler = eventHandler

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.stop()
        self._observer.join()

    def start(self, path):
        print(f"Watching {path}...")
        self._observer.schedule(self._eventHandler, path, recursive=False)
        self._observer.start()

    def stop(self):
        self._observer.stop()
