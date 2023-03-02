from DataAccess.MainConfigData import MainConfigData
import json
import re


class FctHostControlData:
    FIXTURES_ARRAY_KEY = "Fixtures"
    PLC_ID_KEY = "ID"
    PLC_IP_KEY = "PLC_IP"
    PRODUCT_MODELS_KEY = "ProductModels"
    PRODUCT_NAME_KEY = "Name"

    def __init__(self):
        self._mainConfigData = MainConfigData()
        with open(self._mainConfigData.get_fct_host_config_fullpath()) as json_file:
            config = re.sub(r"\s*\/\*.*\*\/", " ", json_file.read())
            self.data = json.loads(config)

    def get_all_fixture_configs(self) -> "list[{}]":
        return self.data[FctHostControlData.FIXTURES_ARRAY_KEY]

    def get_upload_sfc_script_fullpath(self) -> str:
        return self.get_script_fullpath() + self._mainConfigData.get_upload_Sfc_sript()

    def get_script_fullpath(self) -> str:
        productName = self._mainConfigData.get_default_product_name()
        products = self.data[FctHostControlData.PRODUCT_MODELS_KEY]
        for product in products:
            if product[FctHostControlData.PRODUCT_NAME_KEY] == productName:
                return self._extract_script_path(product)
        return ""

    def _extract_script_path(self, product: dict):
        appPath: str = product["Testing_Main"]["App_Path"]
        return appPath.replace("run_test.sh", "")
