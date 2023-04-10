import enum


class TestMode(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str):
        self.description = description

    ONLINE = "Online"
    OFFLINE = "Offline"
    RETEST = "Retest"
    ONLY_REPORT_PASS = "Report Only Pass"
