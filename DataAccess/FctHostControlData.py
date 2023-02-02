import json
from DataAccess.YieldData import YieldData
from Models.Fixture import Fixture


class FctHostControlData:
    CONFIG_JSON_PATH = "config.json"

    def __init__(self):
        self._yieldData = YieldData()

        with open("config.json") as json_file:
            self.data = json.load(json_file)

    def get_fixtures(self):
        fixtures = []
        for fixture in self.data["fixtures"]:
            fixtures.append(
                Fixture(
                    fixture["id"],
                    fixture["ip"],
                    yieldRate=self.get_yield(fixture["id"]),
                )
            )
        return fixtures

    def get_yield(self, ip):
        return self._yieldData.get_yield(ip)
