from gi.repository import GObject
from DataAccess.DisabledFixturesData import DisabledFixturesData
from DataAccess.FctHostControlData import FctHostControlData
from DataAccess.MainConfigData import MainConfigData


class FixtureGridController:
    def __init__(self):
        self.isWatching = False
        self._fctHostControlData = FctHostControlData()
        self._disabledFixturesData = DisabledFixturesData()
        self._mainConfigData = MainConfigData()

    def start_watch_yield(self, task):
        self.periodic(task)
        self.isWatching = True
        GObject.timeout_add(
            self._mainConfigData.get_yield_refresh_ms(),
            lambda: self.periodic(task),
        )

    def get_fixtures(self):
        return self._fctHostControlData.get_fixtures()

    def periodic(self, task):
        fixtures = self.get_fixtures()
        self._disabledFixturesData.save(fixtures)
        task(fixtures)
        return self.isWatching

    def stop_watch_yield(self):
        self.isWatching = False
