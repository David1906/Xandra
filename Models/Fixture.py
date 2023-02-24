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
    ):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate
        self.areLastTestPass = areLastTestPass
        self.isSkipped = isSkipped
        self.yieldErrorMin = yieldErrorMin
        self.yieldWarningMin = yieldWarningMin

    def isDisabled(self) -> bool:
        return self.hasLowYield() and not self.isSkipped and not self.areLastTestPass

    def hasLowYield(self) -> bool:
        return self.yieldRate <= self.yieldErrorMin

    def isWarning(self) -> bool:
        return self.yieldRate <= self.yieldWarningMin or self.isSkipped
