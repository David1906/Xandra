import enum


class LockType(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str):
        self.description = description

    UNLOCKED = "Unlocked"
    LAST_TEST_FAILED = "Failed last {0} tests"
    LOW_YIELD = "Low yield"
