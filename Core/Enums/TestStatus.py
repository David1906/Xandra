import enum


class TestStatus(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str):
        self.description = description

    Initial = "Initial"
    Recovered = "Recovered"
    Idle = "Idle"
    Initialized = "Initialized"
    PreTested = "PreTested"
    Tested = "Tested"
    PreTestFailed = "PreTestFailed"
    Finished = "Finished"
    Pass = "Pass"
    Failed = "Failed"
    Released = "Released"
