import enum


class FixturePlcTestResult(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str):
        self.description = description

    UNKNOWN = "Unknown"
    PASS = "Pass"
    FAILED = "Failed"
    STOP = "Stop"
