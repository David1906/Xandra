import enum


class SettingType(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str):
        self.description = description

    EMPLOYEES_MD5 = "employees md5 last sync"
    LISTS_MD5 = "lists md5 last sync"
