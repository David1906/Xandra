import json, re
from DataAccess.MainConfigData import MainConfigData
from DataAccess.XandraApiData import XandraApiData
from DataAccess.YieldData import YieldData
from Models.Fixture import Fixture


class FctHostControlData:
    FIXTURES_ARRAY_KEY = "Fixtures"
    ID_KEY = "ID"
    PLC_IP_KEY = "PLC_IP"

    def __init__(self):
        self._yieldData = YieldData()
        self._xandraApiData = XandraApiData()
        self._mainConfigData = MainConfigData()

        with open(self._mainConfigData.get_fct_host_config_fullpath()) as json_file:
            config = re.sub(r"\s*\/\*.*\*\/", " ", json_file.read())
            self.data = json.loads(config)

    def get_fixtures(self) -> "list[Fixture]":
        fixtures = []
        yieldErrorMin = self._mainConfigData.get_yield_error_min()
        yieldWarningMin = self._mainConfigData.get_yield_warning_min()
        for fixture in self.data[FctHostControlData.FIXTURES_ARRAY_KEY]:
            fixtureIp = fixture[FctHostControlData.PLC_IP_KEY]
            yieldData = self.get_yieldData(fixtureIp)
            fixtures.append(
                Fixture(
                    fixture[FctHostControlData.ID_KEY],
                    fixtureIp,
                    yieldData["yield"],
                    yieldData["areLastTestPass"],
                    self.get_isSkipped(fixtureIp),
                    yieldErrorMin,
                    yieldWarningMin,
                )
            )
        return fixtures

    def get_yieldData(self, fixtureIp) -> float:
        return self._xandraApiData.getYield(fixtureIp)
        return self._yieldData.get_yield(fixtureIp)

    def get_isSkipped(self, fixtureIp) -> bool:
        return self._yieldData.get_isSkipped(fixtureIp)
