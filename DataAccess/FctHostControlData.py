import json, re
from DataAccess.MainConfigData import MainConfigData
from DataAccess.YieldData import YieldData
from Models.Fixture import Fixture


class FctHostControlData:
    FIXTURES_ARRAY_KEY = "Fixtures"
    ID_KEY = "ID"
    PLC_IP_KEY = "PLC_IP"

    def __init__(self):
        self._yieldData = YieldData()
        self._mainConfigData = MainConfigData()

        with open(self._mainConfigData.get_fct_host_config_fullpath()) as json_file:
            config = re.sub(r"\s*\/\*.*\*\/", " ", json_file.read())
            self.data = json.loads(config)

    def get_fixtures(self) -> "list[Fixture]":
        fixtures = []
        yieldErrorMin = self._mainConfigData.get_yield_error_min()
        yieldWarningMin = self._mainConfigData.get_yield_warning_min()
        for fixture in self.data[FctHostControlData.FIXTURES_ARRAY_KEY]:
            plcIp = fixture[FctHostControlData.PLC_IP_KEY]
            fixtures.append(
                Fixture(
                    fixture[FctHostControlData.ID_KEY],
                    plcIp,
                    self.get_yield(plcIp),
                    self.get_isSkipped(plcIp),
                    yieldErrorMin,
                    yieldWarningMin,
                )
            )
        return fixtures

    def get_yield(self, ip) -> float:
        return self._yieldData.get_yield(ip)

    def get_isSkipped(self, ip) -> bool:
        return self._yieldData.get_isSkipped(ip)
