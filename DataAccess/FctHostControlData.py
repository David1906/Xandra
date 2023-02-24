import json, re
from DataAccess.FixtureData import FixtureData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.TestData import TestData
from Models.Fixture import Fixture


class FctHostControlData:
    FIXTURES_ARRAY_KEY = "Fixtures"
    ID_KEY = "ID"
    PLC_IP_KEY = "PLC_IP"

    def __init__(self):
        self._testData = TestData()
        self._fixtureData = FixtureData()
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
            fixtures.append(
                Fixture(
                    fixture[FctHostControlData.ID_KEY],
                    fixtureIp,
                    self._testData.getYield(fixtureIp),
                    self._testData.areLastTestPass(fixtureIp),
                    self._fixtureData.isSkipped(fixtureIp),
                    yieldErrorMin,
                    yieldWarningMin,
                )
            )
        return fixtures
