class Fixture:
    def __init__(self, id, ip, yieldRate, yieldErrorMin, yieldWarningMin):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate
        self.yieldErrorMin = yieldErrorMin
        self.yieldWarningMin = yieldWarningMin

    def isDisabled(self):
        return self.yieldRate <= self.yieldErrorMin

    def isWarning(self):
        return self.yieldRate <= self.yieldWarningMin
