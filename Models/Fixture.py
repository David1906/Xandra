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
        status: str = "IDLE",
    ):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate
        self.areLastTestPass = areLastTestPass
        self.isSkipped = isSkipped
        self.yieldErrorMin = yieldErrorMin
        self.yieldWarningMin = yieldWarningMin
        self.status = status
        self._test: Test = None

    def is_disabled(self) -> bool:
        return self.has_low_yield() and not self.isSkipped and not self.areLastTestPass

    def has_low_yield(self) -> bool:
        return self.yieldRate <= self.yieldErrorMin

    def is_warning(self) -> bool:
        return self.yieldRate <= self.yieldWarningMin or self.isSkipped

    def set_test(self, test: Test):
        self._test = test

    def get_status_string(self):
        if self._test == None:
            return f"Status: {self.status}"
        return "Result: " + self._test.get_result_string()
