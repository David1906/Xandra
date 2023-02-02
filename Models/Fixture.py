class Fixture:
    YIELD_ERROR_MIN = 80
    YIELD_WARNING_MIN = YIELD_ERROR_MIN + 10

    def __init__(self, id, ip, yieldRate):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate

    def isDisabled(self):
        return self.yieldRate <= Fixture.YIELD_ERROR_MIN

    def isWarning(self):
        return self.yieldRate <= Fixture.YIELD_WARNING_MIN
