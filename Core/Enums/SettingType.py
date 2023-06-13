import enum


class SettingType(enum.Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, description: str, group: str):
        self.group = group
        self.description = description

    EMPLOYEES_LAST_SYNC = "employees last sync", "employees"
    ACTIONS_LAST_SYNC = "actions last sync", "actions"
    SPARE_PARTS_LAST_SYNC = "spare parts last sync", "spare-parts"
