import enum


class FixturePlcStatus(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str):
        self.description = description

    UNKNOWN = "Unknown"
    REQUEST_BOARD_IN = "Request board in"
    TESTING = "Testing"
    TEST_FINISHED = "Test finished"
    REQUEST_BOARD_OUT = "Request board out"