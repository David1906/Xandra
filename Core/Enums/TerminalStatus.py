import enum


class TerminalStatus(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str):
        self.description = description

    STOPPED = "Stopped"
    UNKNOWN = "Unknown"
    IDLE = "IDLE"
    TESTING = "Testing"
    PASS = "Pass"
    FAIL = "Fail"
