from DataAccess.MainConfigData import MainConfigData
from os import fdopen, remove
from shutil import move, copymode
from tempfile import mkstemp
from Utils.PathHelper import PathHelper
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

    def write_check_station_config(self):
        self.write_config(
            "Check_Station",
            [
                ("Enable", '"Enable": true,\n'),
                (
                    "App_Path",
                    f'"App_Path": "{PathHelper().get_root_path()}/Resources/chk_station_is_disabled.py",\n',
                ),
                ("Delay", f'"Delay": 5000\n'),
                ("Timeout", f',"Timeout": 0\n'),
            ],
        )

    def write_test_end_call_config(self):
        self.write_config(
            "Test_End_Call",
            [
                ("Enable", '"Enable": true,\n'),
                (
                    "App_Path",
                    f'"App_Path": "{PathHelper().get_root_path()}/Resources/chk_station_test_finished.py",\n',
                ),
                ("Delay", f'"Delay": 5000\n'),
                ("Timeout", f',"Timeout": 0\n'),
            ],
        )

    def write_config(self, key: str, replaces: "tuple[str,str]"):
        file_path = self._mainConfigData.get_fct_host_config_fullpath()
        fh, abs_path = mkstemp()
        inKey = False
        endKey = False
        with fdopen(fh, "w") as new_file:
            with open(file_path) as old_file:
                for line in old_file:
                    if not inKey:
                        inKey = key.casefold() in line.casefold()
                    elif not endKey:
                        endKey = "},\n" in line
                    text = line
                    if inKey and not endKey:
                        for replace in replaces:
                            key, newLine = replace
                            if key.casefold() in line.casefold():
                                text = " " * (len(line) - len(line.lstrip())) + newLine
                                break
                    new_file.write(text)
        copymode(file_path, abs_path)
        remove(file_path)
        move(abs_path, file_path)

    def get_all_fixture_configs(self) -> "list[{}]":
        return self.data[FctHostControlData.FIXTURES_ARRAY_KEY]

    def get_script_version(self):
        scriptFullPath = self.get_script_fullpath()
        chunks = scriptFullPath.split("/")
        for chunkIdx in range(len(chunks)):
            if chunks[chunkIdx] == "script" and chunkIdx > 0:
                return chunks[chunkIdx - 1]
        return "unknown"

    def get_upload_sfc_script_fullpath(self) -> str:
        return self._mainConfigData.get_upload_Sfc_sript()

    def get_script_fullpath(self) -> str:
        productName = self._mainConfigData.get_default_product_name()
        products = self.data[FctHostControlData.PRODUCT_MODELS_KEY]
        for product in products:
            if bool(
                re.search(productName, product[FctHostControlData.PRODUCT_NAME_KEY])
            ):
                return self._extract_script_path(product)
        return ""

    def _extract_script_path(self, product: dict):
        appPath: str = product["Testing_Main"]["App_Path"]
        appPathSplit = appPath.split("/")
        return "/".join(appPathSplit[0:-1])
