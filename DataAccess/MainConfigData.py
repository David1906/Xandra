import json


class MainConfigData:
    MAIN_CONFIG_JSON_PATH = "xandra_config.json"
    YIELD_WARNING_MAX = 99
    YIELD_WARNING_THRESHOLD_FROM_ERROR = 10

    def _getValue(self, key):
        with open(MainConfigData.MAIN_CONFIG_JSON_PATH) as json_file:
            data = json.load(json_file)
            if type(data) is dict:
                value = data[key]
                if value != None:
                    return value
        return ""

    def get_disabled_fixture_fullpath(self):
        return self._getValue("disabledFixtureJson")

    def get_fixture_ip_env_name(self):
        return self._getValue("fixtureIpEnvironmentName")

    def get_fct_host_control_fullpath(self):
        return self._getValue("fctHostControl")

    def get_yield_error_min(self):
        return self._getValue("yieldErrorThreshold")

    def get_yield_warning_min(self):
        yieldMax = (
            self.get_yield_error_min()
            + MainConfigData.YIELD_WARNING_THRESHOLD_FROM_ERROR
        )
        if yieldMax > MainConfigData.YIELD_WARNING_MAX:
            return MainConfigData.YIELD_WARNING_MAX
        return yieldMax
    
    def get_yield_refresh_ms(self):
        return self._getValue("yieldRefreshSeconds") * 1000
