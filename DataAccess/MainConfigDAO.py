from Utils.Interval import Interval
from Utils.PathHelper import PathHelper
import json
import os


class MainConfigDAO:
    FILE_NAME = (
        "/xandra_config_local.json"
        if os.environ.get("ENV") == "testing"
        else "/xandra_config.json"
    )
    MAIN_CONFIG_JSON_PATH = PathHelper().get_root_path() + FILE_NAME
    YIELD_ERROR_THRESHOLD_INTERVAL = Interval(0, 100)
    YIELD_WARNING_THRESHOLD_INTERVAL = Interval(0, 99)
    YIELD_CALC_QTY_INTERVAL = Interval(0, 1000)
    UNLOCK_PASS_QTY_INTERVAL = Interval(1, 5)
    LOCK_FAIL_QTY_INTERVAL = Interval(0, 10)
    JSON_DATA = {}
    JSON_LAST_MODIFIED = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(MainConfigDAO, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def _get_json_data(self):
        modifiedDate = os.path.getctime(MainConfigDAO.MAIN_CONFIG_JSON_PATH)
        if (
            MainConfigDAO.JSON_LAST_MODIFIED == None
            or modifiedDate > MainConfigDAO.JSON_LAST_MODIFIED
        ):
            with open(MainConfigDAO.MAIN_CONFIG_JSON_PATH) as json_file:
                MainConfigDAO.JSON_DATA = json.load(json_file)
                MainConfigDAO.JSON_LAST_MODIFIED = modifiedDate
        return MainConfigDAO.JSON_DATA

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
        value = self._get_value("yieldErrorThreshold")
        return self.YIELD_ERROR_THRESHOLD_INTERVAL.normalize(value)

    def get_yield_warning_threshold(self) -> float:
        value = self._get_value("yieldWarningThreshold")
        return self.YIELD_WARNING_THRESHOLD_INTERVAL.normalize(value)

    def get_yield_calc_qty(self) -> int:
        value = self._get_value("yieldCalcQty")
        return self.YIELD_CALC_QTY_INTERVAL.normalize(value)

    def get_unlock_pass_qty(self) -> str:
        value = self._get_value("unlockPassQty")
        return self.UNLOCK_PASS_QTY_INTERVAL.normalize(value)

    def get_lock_fail_qty(self) -> str:
        value = self._get_value("lockFailQty")
        return self.LOCK_FAIL_QTY_INTERVAL.normalize(value)

    def get_default_product_name(self) -> "list[str]":
        return self._get_value("defaultProductModelName")

    def get_upload_sfc_script(self) -> str:
        return self._get_value("uploadSfcScript")

    def get_google_isActivated(self):
        return self._get_value("googleSheets")["isActivated"]

    def get_google_sheetName(self):
        return self._get_value("googleSheets")["sheetName"]

    def get_google_maintenanceSheetName(self):
        return self._get_value("googleSheets")["maintenanceSheetName"]

    def get_google_statusLogSheetName(self):
        return self._get_value("googleSheets")["statusLogSheetName"]

    def get_google_syncInterval(self):
        return self._get_value("googleSheets")["syncInterval"]

    def get_google_keyfilePath(self, no: int = 0):
        return self._get_value("googleSheets")[
            f"keyfilePath{'' if no <=0 else str(no)}"
        ]

    def get_maintenance_parts(self):
        return self._get_value("maintenanceParts")

    def get_maintenance_actions(self):
        return self._get_value("maintenanceActions")
