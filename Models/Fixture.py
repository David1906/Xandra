from Models.Test import Test


class Fixture:
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
    ):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate
        self.areLastTestPass = areLastTestPass
        self.isSkipped = isSkipped
        self.yieldErrorMin = yieldErrorMin
        self.yieldWarningMin = yieldWarningMin
        self.isTesting = isTesting
        self._test: Test = None

    def is_disabled(self) -> bool:
        return self.has_low_yield() and not self.isSkipped and not self.areLastTestPass

    def has_low_yield(self) -> bool:
        return self.yieldRate <= self.yieldErrorMin

    def is_warning(self) -> bool:
        return self.yieldRate <= self.yieldWarningMin

    def set_test(self, test: Test):
        self._test = test

    def set_isTesting(self, isTesting: bool):
        self.isTesting = isTesting
        self._test = None

    def get_status_string(self):
        if self._test == None:
            return f"Status: {self.get_status_text()}"
        return f"SN: {self._test.serialNumber}      Result: {self._test.get_result_string()}"

    def get_status_text(self):
        return "Testing" if self.isTesting else "IDLE"

    def get_status_color(self) -> str:
        if self.isSkipped:
            return "gray"
        if self.is_disabled():
            return "lightcoral"
        elif self.is_warning():
            return "yellow"
        return ""
