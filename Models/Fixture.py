class Fixture:
    def __init__(self, id, ip, yieldRate, isSkipped, yieldErrorMin, yieldWarningMin):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate
        self.isSkipped = isSkipped
        self.yieldErrorMin = yieldErrorMin
        self.yieldWarningMin = yieldWarningMin

    def isDisabled(self):
        return self.hasLowYield() and not self.isSkipped

    def hasLowYield(self):
        return self.yieldRate <= self.yieldErrorMin

    def isWarning(self):
        return self.yieldRate <= self.yieldWarningMin or self.isSkipped
