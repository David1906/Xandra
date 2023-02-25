from DataAccess.MainConfigData import MainConfigData
import json
import re


class FctHostControlData:
    FIXTURES_ARRAY_KEY = "Fixtures"
    PLC_ID_KEY = "ID"
    PLC_IP_KEY = "PLC_IP"

    def __init__(self):
        self._mainConfigData = MainConfigData()
        with open(self._mainConfigData.get_fct_host_config_fullpath()) as json_file:
            config = re.sub(r"\s*\/\*.*\*\/", " ", json_file.read())
            self.data = json.loads(config)

    def get_all_fixture_configs(self) -> "list[{}]":
        return self.data[FctHostControlData.FIXTURES_ARRAY_KEY]
