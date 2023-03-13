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
    ):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate
        self.areLastTestPass = areLastTestPass
        self.isSkipped = isSkipped
        self.yieldErrorMin = yieldErrorMin
        self.yieldWarningMin = yieldWarningMin
        self.isTesting = isTesting
        self.isRetestMode = isRetestMode

    def is_disabled(self) -> bool:
        return (
            self.has_low_yield() and self.is_lock_enabled() and not self.areLastTestPass
        )

    def is_lock_enabled(self):
        return self.isSkipped == self.isRetestMode or (
            not self.isSkipped and self.isRetestMode
        )

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
            return "gray"
        if self.is_disabled():
            return "lightcoral"
        elif self.is_warning():
            return "yellow"
        return ""

    def reset(self):
        self.isTesting = False
        self.isRetestMode = False
        self.isSkipped = False

    def __str__(self):
        return f"id: {self.id} ip: {self.ip} yieldRate: {self.yieldRate} areLastTestPass: {self.areLastTestPass} isSkipped: {self.isSkipped} yieldErrorMin: {self.yieldErrorMin} yieldWarningMin: {self.yieldWarningMin} isTesting: {self.isTesting} isRetestMode: {self.isRetestMode}"
