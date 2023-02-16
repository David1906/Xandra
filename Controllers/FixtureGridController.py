from typing import Callable
from PyQt5 import QtCore
from DataAccess.DisabledFixturesData import DisabledFixturesData
from DataAccess.FctHostControlData import FctHostControlData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.YieldData import YieldData
from Models.Fixture import Fixture


class FixtureGridController:
    def __init__(self):
        self.isWatching = False
        self._fctHostControlData = FctHostControlData()
        self._disabledFixturesData = DisabledFixturesData()
        self._yieldData = YieldData()
        self._mainConfigData = MainConfigData()

    def start_watch_yield(self, task: Callable[["list[Fixture]"], None]):
        self.periodic(task)
        self.isWatching = True
        try:
            self._updateTimer.stop()
        except:
            pass
        self._updateTimer = QtCore.QTimer()
        self._updateTimer.timeout.connect(lambda: self.periodic(task))
        self._updateTimer.start(self._mainConfigData.get_yield_refresh_ms())

    def get_fixtures(self) -> "list[Fixture]":
        return self._fctHostControlData.get_fixtures()

    def periodic(self, task: Callable[["list[Fixture]"], None]) -> bool:
        fixtures = self.get_fixtures()

        for fixture in fixtures:
            if not fixture.hasLowYield():
                self._yieldData.update_yield_lock_skipped(fixture)
                fixture.isSkipped = False
        self._disabledFixturesData.save(fixtures)
        task(fixtures)
        return self.isWatching

    def stop_watch_yield(self):
        self.isWatching = False
