import json
from DataAccess.MainConfigData import MainConfigData
from DataAccess.YieldData import YieldData
from Models.Fixture import Fixture


class FctHostControlData:
    CONFIG_JSON_PATH = "config.json"

    def __init__(self):
        self._yieldData = YieldData()
        self._mainConfigData = MainConfigData()

        with open(FctHostControlData.CONFIG_JSON_PATH) as json_file:
            self.data = json.load(json_file)

    def get_fixtures(self):
        fixtures = []
        yieldErrorMin = self._mainConfigData.get_yield_error_min()
        yieldWarningMin = self._mainConfigData.get_yield_warning_min()
        for fixture in self.data["fixtures"]:
            fixtures.append(
                Fixture(
                    fixture["id"],
                    fixture["ip"],
                    self.get_yield(fixture["id"]),
                    yieldErrorMin,
                    yieldWarningMin,
                )
            )
        return fixtures

    def get_yield(self, ip):
        return self._yieldData.get_yield(ip)
