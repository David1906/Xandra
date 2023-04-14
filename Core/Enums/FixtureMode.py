import enum


class FixtureMode(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(
        self,
        description: str,
        isLockEnabled: bool = False,
        uploadToSfcPass: bool = False,
        uploadToSfcFail: bool = False,
    ):
        self.description = description
        self.isLockEnabled = isLockEnabled
        self.uploadToSfcPass = uploadToSfcPass
        self.uploadToSfcFail = uploadToSfcFail

    def is_upload_to_sfc(self, status: bool):
        if status:
            return self.uploadToSfcPass
        return self.uploadToSfcFail

    UNKNOWN = "Unknown", True
    ONLINE = "Online", True
    OFFLINE = "Offline"
    RETEST = "Retest"
    ONLY_REPORT_PASS = "Only Report Pass", True, True
