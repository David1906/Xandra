import json
import os


class MainConfigData:
    MAIN_CONFIG_JSON_PATH = "xandra_config_local.json"
    YIELD_WARNING_MAX = 99
    YIELD_WARNING_THRESHOLD_FROM_ERROR = 10
    JSON_DATA = {}
    JSON_LAST_MODIFIED = None

    def _getJsonData(self):
        modifiedDate = os.path.getctime(MainConfigData.MAIN_CONFIG_JSON_PATH)
        if (
            MainConfigData.JSON_LAST_MODIFIED == None
            or modifiedDate > MainConfigData.JSON_LAST_MODIFIED
        ):
            with open(MainConfigData.MAIN_CONFIG_JSON_PATH) as json_file:
                MainConfigData.JSON_DATA = json.load(json_file)
                MainConfigData.JSON_LAST_MODIFIED = modifiedDate
        return MainConfigData.JSON_DATA

    def _getValue(self, key: str):
        data = self._getJsonData()
        if type(data) is dict:
            value = data[key]
            if value != None:
                return value
        return ""

    def get_disabled_fixture_fullpath(self) -> str:
        return self._getValue("disabledFixturesJson")

    def get_fixture_ip_env_name(self) -> str:
        return self._getValue("fixtureIpEnvironmentName")

    def get_fct_host_control_fullpath(self) -> str:
        return self._getValue("fctHostControl")

    def get_yield_error_min(self) -> float:
        return self._getValue("yieldErrorThreshold")

    def get_yield_warning_min(self) -> float:
        yieldMax = (
            self.get_yield_error_min()
            + MainConfigData.YIELD_WARNING_THRESHOLD_FROM_ERROR
        )
        if yieldMax > MainConfigData.YIELD_WARNING_MAX:
            return MainConfigData.YIELD_WARNING_MAX
        return yieldMax

    def get_yield_refresh_ms(self) -> int:
        return self._getValue("yieldRefreshSeconds") * 1000

    def get_fct_host_config_fullpath(self) -> str:
        return self._getValue("fctHostControlConfig")

    def get_xandra_api_url(self) -> str:
        return self._getValue("xandraApiUrl")

    def get_yield_calc_qty(self) -> int:
        return self._getValue("yieldCalcQty")

    def get_last_test_pass_qty(self) -> str:
        return self._getValue("lastTestPassQty")
    
    def get_logs_path(self) -> str:
        return self._getValue("logsPath")
