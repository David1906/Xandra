import os
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

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(FctHostControlData, cls).__new__(cls, *args, **kwargs)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if self.initialized:
            return
        else:
            self.initialized = True

        self.configIdx = 0
        self._mainConfigData = MainConfigData()

        self.load_data_from_first_valid_config()

    def load_data_from_first_valid_config(self):
        self.configIdx = self.get_first_valid_fct_host_config_index()
        with open(
            self._mainConfigData.get_fct_host_config_fullpath(self.configIdx)
        ) as json_file:
            config = re.sub(r"\s*\/\*.*\*\/", " ", json_file.read())
            self.data = json.loads(config)

    def get_first_valid_fct_host_config_index(self) -> str:
        for idx in range(self._mainConfigData.get_fct_host_control_len()):
            if os.path.exists(self._mainConfigData.get_fct_host_config_fullpath(idx)):
                return idx
        return 0

    def write_check_station_config(self):
        self.write_config(
            "Check_Station",
            [
                ("Enable", "true"),
                (
                    "App_Path",
                    f'"{PathHelper().get_root_path()}/Resources/chk_station_is_disabled.py"',
                ),
                ("Delay", f"5000"),
                ("Timeout", f"0"),
            ],
        )

    def write_test_end_call_config(self):
        self.write_config(
            "Test_End_Call",
            [
                ("Enable", "true"),
                (
                    "App_Path",
                    f'"{PathHelper().get_root_path()}/Resources/chk_station_test_finished.py"',
                ),
                ("Delay", f"5000"),
                ("Timeout", f'0'),
            ],
        )

    def write_config(self, key: str, replaces: "tuple[str,str]"):
        file_path = self._mainConfigData.get_fct_host_config_fullpath(self.configIdx)
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
                            key, newValue = replace
                            if key.casefold() in line.casefold():
                                text = self.replace_value(line, newValue)
                                break
                    new_file.write(text)
        copymode(file_path, abs_path)
        remove(file_path)
        move(abs_path, file_path)

    def replace_value(self, line: str, newValue: str):
        start = line.find(":") + 1
        end = len(line)
        match = re.search("(\/\*)|,|\n|}", line)
        if match:
            end = match.start()
        return "%s %s %s" % (line[:start], newValue, line[end:])

    def get_all_fixture_configs(self) -> "list[dict]":
        return self.data[FctHostControlData.FIXTURES_ARRAY_KEY]

    def get_script_version(self):
        scriptFullPath = self.get_script_fullpath()
        chunks = scriptFullPath.split("/")
        for chunkIdx in range(len(chunks)):
            if chunks[chunkIdx] == "script" and chunkIdx > 0:
                return chunks[chunkIdx - 1]
        return "unknown"

    def get_fct_host_control_executable_fullpath(self) -> str:
        return self._mainConfigData.get_fct_host_control_executable_fullpath(
            self.configIdx
        )

    def get_upload_sfc_script_fullpath(self) -> str:
        return self._mainConfigData.get_upload_sfc_script(self.configIdx)

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
