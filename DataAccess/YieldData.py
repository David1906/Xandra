import json

from DataAccess.MainConfigData import MainConfigData
from Models.Fixture import Fixture


class YieldData:
    YIELD_JSON_PATH = "./Resources/yield.json"
    YIELD_LOCK_SKIPED_JSON_PATH = "./Resources/yield_lock_skipped.json"

    def __init__(self) -> None:
        self._mainConfigData = MainConfigData()

    def get_yield(self, ip):
        return self._getValue(ip, YieldData.YIELD_JSON_PATH)

    def get_isSkipped(self, ip):
        return self._getValue(ip, YieldData.YIELD_LOCK_SKIPED_JSON_PATH) == True

    def _getValue(self, key, source):
        with open(source) as json_file:
            data = json.load(json_file)
            if type(data) is dict:
                if key in data:
                    return data[key]
        return ""

    def update_yield_lock_skipped(self, fixture):
        with open(YieldData.YIELD_LOCK_SKIPED_JSON_PATH, "r") as jsonFile:
            data = json.load(jsonFile)

        data[fixture.ip] = fixture.isSkipped

        with open(YieldData.YIELD_LOCK_SKIPED_JSON_PATH, "w") as jsonFile:
            json.dump(data, jsonFile)
