from Core.Enums.LockType import LockType
from Core.Enums.TestMode import TestMode


class FixtureConfig:
    def __init__(
        self,
        id: int = 0,
        ip: int = 0,
        yieldRate: float = 0,
        areLastTestPass: bool = False,
        isSkipped: bool = False,
        yieldErrorMin: float = 0,
        yieldWarningMin: float = 0,
        isTesting: bool = False,
        isRetestMode: bool = False,
        areLastTestFail: bool = False,
        enableLock: bool = True,
        lockFailQty: int = 0,
    ):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate
        self.areLastTestPass = areLastTestPass
        self.areLastTestFail = areLastTestFail
        self.isSkipped = isSkipped
        self.yieldErrorMin = yieldErrorMin
        self.yieldWarningMin = yieldWarningMin
        self.isTesting = isTesting
        self.isRetestMode = isRetestMode
        self.enableLock = enableLock
        self.lockFailQty = lockFailQty

    def get_lock(self) -> LockType:
        if not self.is_lock_enabled():
            return LockType.UNLOCKED
        if self.areLastTestPass:
            return LockType.UNLOCKED
        if self.areLastTestFail:
            return LockType.LAST_TEST_FAILED
        if self.has_low_yield():
            return LockType.LOW_YIELD
        return LockType.UNLOCKED

    def get_lock_description(self) -> str:
        lock = self.get_lock()
        if lock == LockType.LAST_TEST_FAILED:
            return self.get_lock().description.format(self.lockFailQty)
        return self.get_lock().description

    def is_lock_enabled(self):
        if not self.enableLock:
            return False
        return self.isSkipped == self.isRetestMode or (
            not self.isSkipped and self.isRetestMode
        )

    def is_disabled(self) -> bool:
        return self.get_lock() != LockType.UNLOCKED

    def has_low_yield(self) -> bool:
        return self.yieldRate <= self.yieldErrorMin

    def is_warning(self) -> bool:
        return self.yieldRate <= self.yieldWarningMin

    def set_isTesting(self, isTesting: bool):
        self.isTesting = isTesting
        if isTesting:
            self._test = None

    def get_status_text(self):
        return "Testing" if self.isTesting else "IDLE"

    def get_status_color(self) -> str:
        if self.isRetestMode and self.is_disabled():
            return "lightcoral"
        if self.isRetestMode:
            return "orange"
        if self.isSkipped:
            return "#B8B8B8"
        if self.is_disabled():
            return "lightcoral"
        elif self.is_warning():
            return "#DED851"
        return ""

    def get_mode(self) -> TestMode:
        if self.isSkipped and self.isRetestMode:
            return TestMode.ONLY_REPORT_PASS
        if self.isRetestMode:
            return TestMode.RETEST
        if self.isSkipped:
            return TestMode.OFFLINE
        return TestMode.ONLINE

    def reset(self):
        self.isTesting = False
        self.isRetestMode = False
        self.isSkipped = False

    def __str__(self):
        return f"id: {self.id} ip: {self.ip} yieldRate: {self.yieldRate} areLastTestPass: {self.areLastTestPass} isSkipped: {self.isSkipped} yieldErrorMin: {self.yieldErrorMin} yieldWarningMin: {self.yieldWarningMin} isTesting: {self.isTesting} isRetestMode: {self.isRetestMode}"
