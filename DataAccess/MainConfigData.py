from Utils.PathHelper import PathHelper
import json
import os


class MainConfigData:
    FILE_NAME = (
        "/xandra_config_local.json"
        if os.environ.get("ENV") == "testing"
        else "/xandra_config.json"
    )
    MAIN_CONFIG_JSON_PATH = PathHelper().get_root_path() + FILE_NAME
    YIELD_WARNING_MAX = 99
    YIELD_WARNING_THRESHOLD_FROM_ERROR = 10
    JSON_DATA = {}
    JSON_LAST_MODIFIED = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(MainConfigData, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def _get_json_data(self):
        modifiedDate = os.path.getctime(MainConfigData.MAIN_CONFIG_JSON_PATH)
        if (
            MainConfigData.JSON_LAST_MODIFIED == None
            or modifiedDate > MainConfigData.JSON_LAST_MODIFIED
        ):
            with open(MainConfigData.MAIN_CONFIG_JSON_PATH) as json_file:
                MainConfigData.JSON_DATA = json.load(json_file)
                MainConfigData.JSON_LAST_MODIFIED = modifiedDate
        return MainConfigData.JSON_DATA

    def _get_value(self, key: str):
        data = self._get_json_data()
        if type(data) is dict:
            value = data[key]
            if value != None:
                return value
        return ""

    def get_fixture_ip_env_name(self) -> str:
        return self._get_value("fixtureIpEnvironmentName")

    def get_fct_host_control(self) -> str:
        return self._get_value("fctHostControl")

    def get_fct_host_control_len(self) -> int:
        return len(self.get_fct_host_control())

    def get_fct_host_control_path(self, index: int = 0) -> str:
        return self.get_fct_host_control()[index]["path"]

    def get_fct_host_control_executable_fullpath(self, index: int = 0) -> str:
        return (
            self.get_fct_host_control_path(index)
            + "/"
            + self.get_fct_host_control()[index]["executable"]
        )

    def get_fct_host_config_fullpath(self, index: int = 0) -> str:
        return (
            self.get_fct_host_control_path(index)
            + "/"
            + self.get_fct_host_control()[index]["config"]
        )

    def get_logs_path(self) -> str:
        return self._get_value("logsPath")

    def get_yield_error_threshold(self) -> float:
        return self._get_value("yieldErrorThreshold")

    def get_yield_warning_threshold(self) -> float:
        yieldWarning = self._get_value("yieldWarningThreshold")
        if yieldWarning > MainConfigData.YIELD_WARNING_MAX:
            return MainConfigData.YIELD_WARNING_MAX
        return yieldWarning

    def get_yield_calc_qty(self) -> int:
        return self._get_value("yieldCalcQty")

    def get_unlock_pass_qty(self) -> str:
        return self._get_value("unlockPassQty")

    def get_lock_fail_qty(self) -> str:
        return self._get_value("lockFailQty")

    def get_default_product_name(self) -> "list[str]":
        return self._get_value("defaultProductModelName")

    def get_upload_Sfc_sript(self) -> str:
        return self._get_value("uploadSfcScript")

    def get_google_isActivated(self):
        return self._get_value("googleSheets")["isActivated"]

    def get_google_sheetName(self):
        return self._get_value("googleSheets")["sheetName"]

    def get_google_keyfilePath(self):
        return self._get_value("googleSheets")["keyfilePath"]
