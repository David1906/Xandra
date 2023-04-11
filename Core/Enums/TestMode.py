import enum


class TestMode(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str, isLockEnabled: bool, uploadToSfc: bool):
        self.description = description
        self.isLockEnabled = isLockEnabled
        self.uploadToSfc = uploadToSfc

    UNKNOWN = "Unknown", True, False
    ONLINE = "Online", True, False
    OFFLINE = "Offline", False, False
    RETEST = "Retest", False, False
    ONLY_REPORT_PASS = "Report Only Pass", True, True
