class Fixture:
    def __init__(
        self,
        id: int,
        ip: int,
        yieldRate: float,
        isSkipped: bool,
        yieldErrorMin: float,
        yieldWarningMin: float,
    ):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate
        self.isSkipped = isSkipped
        self.yieldErrorMin = yieldErrorMin
        self.yieldWarningMin = yieldWarningMin

    def isDisabled(self) -> bool:
        return self.hasLowYield() and not self.isSkipped

    def hasLowYield(self) -> bool:
        return self.yieldRate <= self.yieldErrorMin

    def isWarning(self) -> bool:
        return self.yieldRate <= self.yieldWarningMin or self.isSkipped
