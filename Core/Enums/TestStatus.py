import enum


class TestStatus(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str):
        self.description = description

    def is_testing(self) -> bool:
        return self == TestStatus.Tested

    Initialized = "Initial"
    Idle = "Idle"
    BoardLoaded = "Board loaded"
    Tested = "Tested"
    Finished = "Finished"
