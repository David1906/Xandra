import enum


class BoardPlcStatus(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str):
        self.description = description

    @staticmethod
    def get_description(value: int):
        description = ""
        try:
            description = BoardPlcStatus(value).description
        except:
            description = "Unknown"
        return f"({value}) {description}"

    NONE = "None"
    UNKNOWN_1 = "Unknown"
    REQUEST_UUT = "Request UUT"
    UUT_LOADING = "UUT Loading"
    TAU_READY = "TAU Ready"
    UUT_POWERING = "UUT Powering"
    UUT_POWERED = "UUT Powered"
    UNKNOWN_7 = "Unknown"
    UNKNOWN_8 = "Unknown"
    TAU_UNLOADING = "TAU Unloading"
    TAU_RELEASED = "Released"
    UNKNOWN_11 = "Unknown"
    UNKNOWN_12 = "Unknown"
    UNKNOWN_13 = "Unknown"
    UNKNOWN_14 = "Unknown"
    UNKNOWN_15 = "Unknown"
    UUT_UNLOADING = "UUT Unloading"
