from __future__ import annotations
from Core.Enums.FixtureMode import FixtureMode
from Core.Enums.FixtureStatus import FixtureStatus
from Core.Enums.LockType import LockType
from datetime import datetime, timedelta
from Models.Test import Test
from PyQt5 import QtCore
from timeit import default_timer as timer
import math


class Fixture(QtCore.QObject):
    OVER_ELAPSED_THRESHOLD = timedelta(hours=1, minutes=45)
    SEND_STATUS_CHANGE_THRESHOLD = timedelta(minutes=20)
    status_change = QtCore.pyqtSignal(FixtureStatus, datetime, timedelta, FixtureStatus)
    update = QtCore.pyqtSignal()
    over_elapsed = QtCore.pyqtSignal()
    testing_tick = QtCore.pyqtSignal(timedelta)

    def __init__(
        self,
        id: int,
        ip: str,
        yieldErrorThreshold: float,
        yieldWarningThreshold: float,
        lockFailQty: int,
        unlockPassQty: int,
        mode: FixtureMode = FixtureMode.UNKNOWN,
        tests: "list[Test]" = [],
    ) -> None:
        super().__init__()

        self._id = id
        self._ip = ip
        self._yieldErrorThreshold = yieldErrorThreshold
        self._yieldWarningThreshold = yieldWarningThreshold
        self._lockFailQty = lockFailQty
        self._unlockPassQty = unlockPassQty
        self._mode = mode
        self._tests = tests
        self.lastTest = Test(isNull=True)
        self._isTesting = False
        self._isStarted = False
        self._isLockEnabled = False
        self._wasOverElapsed = False
        self._startDateTime = datetime.now()
        self._startTimer = timer()

        self._shouldUpdateRemainingToUnlock = True
        self._lastRemainingToUnlock = 0
        self._shouldUpdateLock = True
        self._lastLock = LockType.UNLOCKED
        self._shouldUpdateYield = True
        self._lastYield = 0.0
        self._lastStatus = FixtureStatus.UNKNOWN
        self.lastLockDescription = ""

        self._updateTimer = QtCore.QTimer()
        self._updateTimer.timeout.connect(self._on_tick)
        self._updateTimer.start(1000)

    def _on_tick(self):
        elapsed = self.get_elapsed_time()
        if self.isTesting:
            if not self._wasOverElapsed and self.is_over_elapsed(elapsed):
                self._wasOverElapsed = True
                self.over_elapsed.emit()
            self.testing_tick.emit(elapsed)

        if elapsed >= Fixture.SEND_STATUS_CHANGE_THRESHOLD:
            self.emit_status_change()

    def should_abort_test(self):
        if self.mode == FixtureMode.OFFLINE:
            return False
        return self.is_locked()

    def is_locked(self) -> str:
        return self.get_lock() != LockType.UNLOCKED

    def get_lock(self) -> LockType:
        if self._shouldUpdateLock:
            self._shouldUpdateLock = False
            if not self.isLockEnabled or self.mode == FixtureMode.RETEST:
                self._lastLock = LockType.UNLOCKED
            elif self.are_last_tests_pass():
                self._lastLock = LockType.UNLOCKED
            elif self._has_low_yield() and self._yieldErrorThreshold > 0:
                self._lastLock = LockType.LOW_YIELD
            elif self._are_last_tests_fail() and self._lockFailQty > 0:
                self._lastLock = LockType.LAST_TEST_FAILED
            else:
                self._lastLock = LockType.UNLOCKED
        return self._lastLock

    def get_lock_description(self) -> str:
        lock = self.get_lock()
        if lock == LockType.LAST_TEST_FAILED:
            self.lastLockDescription = lock.description.format(self.lockFailQty)
        elif lock == LockType.LOW_YIELD:
            self.lastLockDescription = lock.description.format(self.get_yield())
        else:
            self.lastLockDescription = lock.description
        return self.lastLockDescription

    def are_last_tests_pass(self) -> bool:
        return self.get_remaining_to_unlock() <= 0

    def get_remaining_to_unlock(self) -> bool:
        if self._shouldUpdateRemainingToUnlock:
            self._shouldUpdateRemainingToUnlock = False
            totalPass = 0
            for test in self.tests[: self.get_min_tests_qty() - 1]:
                if test.status:
                    totalPass = totalPass + 1
            remaining = self._unlockPassQty - totalPass
            if len(self.tests) < self._unlockPassQty or remaining <= 0:
                remaining = 0
            elif self.tests[0].status == False:
                remaining = self._unlockPassQty
            self._lastRemainingToUnlock = remaining
        return self._lastRemainingToUnlock

    def _has_low_yield(self) -> bool:
        return self.get_yield() <= self._yieldErrorThreshold

    def get_yield(self) -> float:
        if self._shouldUpdateYield:
            self._shouldUpdateYield = False
            if len(self.tests) == 0:
                self._lastYield = 100
            else:
                passTests = 0
                for test in self.tests:
                    if test.status:
                        passTests += 1
                self._lastYield = round((passTests / len(self.tests)) * 100, 2)
        return self._lastYield

    def _are_last_tests_fail(self) -> bool:
        if self._lockFailQty == 0 or len(self.tests) < self._lockFailQty:
            return False
        total = 0
        maxTotal = 0
        for test in self.tests[: self.get_min_tests_qty()]:
            if not test.status:
                total = total + 1
            else:
                total = 0
            maxTotal = maxTotal if maxTotal > total else total
        return maxTotal >= self.lockFailQty

    def is_over_elapsed(self, elapsed: timedelta = None) -> bool:
        if not self.isTesting:
            return False
        if elapsed == None:
            elapsed = self.get_elapsed_time()
        return elapsed > Fixture.OVER_ELAPSED_THRESHOLD

    def get_elapsed_time(self) -> timedelta:
        return timedelta(seconds=math.floor(timer() - self._startTimer))

    def get_status_message(self) -> str:
        payload = ""
        status = self.get_status()
        if status == FixtureStatus.TESTING:
            payload = f"({str(self.get_elapsed_time())})"
        elif not self.lastTest.isNull:
            payload = f"SN: {self.lastTest.serialNumber}    Result: {self.lastTest.get_result_string()}"
        return f"{status.description}{'' if len(payload) == 0 else ' - '}{payload}"

    def get_status(self) -> FixtureStatus:
        if self.is_locked():
            return FixtureStatus.LOCKED
        if self.isTesting:
            return FixtureStatus.TESTING
        return FixtureStatus.IDLE

    def is_upload_to_sfc(self, test: Test) -> bool:
        return self.mode.is_upload_to_sfc(test.status)

    def get_color(self) -> bool:
        if self.mode == FixtureMode.OFFLINE:
            return "#B8B8B8"
        if self.mode == FixtureMode.RETEST:
            return "orange"
        if self.is_locked():
            return "lightcoral"
        elif self._is_warning():
            return "#DED851"
        return ""

    def _is_warning(self) -> bool:
        return self.get_yield() <= self._yieldWarningThreshold

    def equals(self, fixture: Fixture) -> bool:
        return fixture.ip == self.ip

    def equalsIp(self, fixtureIp: str) -> bool:
        return self.ip == fixtureIp

    def copy_configs(self, fixture: Fixture):
        self._yieldErrorThreshold = fixture._yieldErrorThreshold
        self._yieldWarningThreshold = fixture._yieldWarningThreshold
        self._lockFailQty = fixture._lockFailQty
        self._unlockPassQty = fixture._unlockPassQty
        self._property_changed(updateCalcs=True)

    def _property_changed(self, updateCalcs=False):
        if updateCalcs:
            self._shouldUpdateRemainingToUnlock = True
            self._shouldUpdateLock = True
            self._shouldUpdateYield = True
        self.emit_status_change()
        self.update.emit()

    def emit_status_change(self, force: bool = False):
        status = self.get_status()
        if status != self._lastStatus or force:
            self.status_change.emit(
                self._lastStatus, self._startDateTime, self.get_elapsed_time(), status
            )
            self._startDateTime = datetime.now()
            self._startTimer = timer()
            self._lastStatus = status

    def can_start(self) -> bool:
        canStart = not self.is_locked() or self.mode == FixtureMode.OFFLINE
        return canStart and not self.isStarted

    def can_change_traceability(self) -> bool:
        return not self.mode == FixtureMode.RETEST and not self.isStarted

    def can_change_retest(self) -> bool:
        isLocked = self.is_locked()
        if self.mode == FixtureMode.OFFLINE:
            isLocked = not self.are_last_tests_pass()
        return not isLocked and not self.isStarted

    def get_min_tests_qty(self) -> int:
        return self._lockFailQty + self._unlockPassQty

    @property
    def id(self) -> int:
        return self._id

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def mode(self) -> FixtureMode:
        return self._mode

    @mode.setter
    def mode(self, value: FixtureMode):
        self._mode = value
        self._property_changed(updateCalcs=True)

    @property
    def tests(self) -> "list[Test]":
        return self._tests

    @tests.setter
    def tests(self, value: "list[Test]"):
        if value == None:
            value = []
        self._tests = value
        self._property_changed(updateCalcs=True)

    @property
    def isTesting(self) -> bool:
        return self._isTesting

    @isTesting.setter
    def isTesting(self, value: bool):
        self._isTesting = value
        if self._isTesting:
            self._wasOverElapsed = False
            self.lastTest = Test(isNull=True)

        self._property_changed()

    @property
    def isLockEnabled(self) -> bool:
        return self._isLockEnabled

    @isLockEnabled.setter
    def isLockEnabled(self, value: bool):
        self._isLockEnabled = value
        self._shouldUpdateLock = True
        self._property_changed()

    @property
    def isStarted(self) -> bool:
        return self._isStarted

    @isStarted.setter
    def isStarted(self, value: bool):
        self._isStarted = value
        self._property_changed()

    @property
    def lockFailQty(self) -> bool:
        return self._lockFailQty
