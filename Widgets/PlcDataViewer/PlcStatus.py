from Core.Enums.BoardPlcStatus import BoardPlcStatus
from Core.Enums.FixturePlcStatus import FixturePlcStatus
from Core.Enums.FixturePlcTestResult import FixturePlcTestResult
from Widgets.PlcDataViewer.PlcAddress import PlcAdress


class PlcStatus:
    EMPTY_STR = "Empty"

    def __init__(self) -> None:
        self.mac = ""
        self.sn = ""
        self.board_status = ""
        self.device_no = ""
        self.mode = ""
        self.heartbeat = ""
        self.test_no = ""
        self.test_result = ""
        self.request_mode = ""
        self.return_mode = ""
        self.send_in_out_enable = ""
        self.fixture_status = ""
        self.lifter = ""
        self.scan = ""
        self.fixture_error = ""
        self.tccs_task_no = ""
        self.model_id = ""
        self.fixture_id = ""

    def set_holding_registers(self, rawData: "list(int)"):
        self.mac = self._raw_data_to_str(rawData, PlcAdress.MAC, PlcAdress.MAC_LEN)
        self.sn = self._raw_data_to_str(rawData, PlcAdress.SN, PlcAdress.SN_LEN)
        self.board_status = self._extract_single_address(
            rawData, PlcAdress.BOARD_STATUS
        )
        self.device_no = self._extract_single_address(rawData, PlcAdress.DEVICE_NO)
        self.mode = self._extract_single_address(rawData, PlcAdress.MODE)
        self.heartbeat = self._extract_single_address(rawData, PlcAdress.HEARTBEAT)
        self.test_no = self._extract_single_address(rawData, PlcAdress.TEST_NO)
        self.test_result = self._extract_single_address(rawData, PlcAdress.TEST_RESULT)
        self.request_mode = self._extract_single_address(
            rawData, PlcAdress.REQUEST_MODE
        )
        self.return_mode = self._extract_single_address(rawData, PlcAdress.RETURN_MODE)
        self.send_in_out_enable = self._extract_single_address(
            rawData, PlcAdress.SEND_IN_OUT_ENABLE
        )
        self.fixture_status = self._extract_single_address(
            rawData, PlcAdress.FIXTURE_STATUS
        )
        self.lifter = self._extract_single_address(rawData, PlcAdress.LIFTER)
        self.scan = self._extract_single_address(rawData, PlcAdress.SCAN)
        self.fixture_error = self._extract_single_address(
            rawData, PlcAdress.FIXTURE_ERROR
        )
        self.tccs_task_no = self._raw_data_to_str(
            rawData, PlcAdress.TCCS_TASK_NO, PlcAdress.TCCS_TASK_NO_LEN
        )
        self.model_id = self._raw_data_to_str(
            rawData, PlcAdress.MODEL_ID, PlcAdress.MODEL_ID_LEN
        )
        self.fixture_id = self._raw_data_to_str(
            rawData, PlcAdress.FIXTURE_ID, PlcAdress.FIXTURE_ID_LEN
        )

    def _raw_data_to_str(
        self, rawData: "list(int)", startAddr: int, len: int = 1
    ) -> str:
        chunk = self._extract_chunk(rawData, startAddr, len)
        asciiChunk = list(filter(lambda x: x != 0, chunk))
        string = "".join(self._ascii_to_char(asciiChunk))
        return self.EMPTY_STR if string == "" else string

    def _extract_single_address(self, rawData: "list(int)", startAddr: int) -> int:
        return self._extract_chunk(rawData, startAddr)[0]

    def _extract_chunk(
        self, rawData: "list(int)", startAddr: int, len: int = 1
    ) -> "list(int)":
        start = startAddr - PlcAdress.START_ADDR
        return rawData[start : start + len]

    def _ascii_to_char(self, ascii: "list(int)"):
        return [chr(character) for character in ascii]

    def is_board_loaded(self) -> bool:
        return self.sn != self.EMPTY_STR and not self.is_board_released()

    def is_board_released(self) -> bool:
        return self.board_status in [
            BoardPlcStatus.TAU_RELEASED.value,
            BoardPlcStatus.UUT_UNLOADING.value,
            BoardPlcStatus.TAU_UNLOADING.value,
        ]

    def is_testing(self) -> bool:
        return self.fixture_status == FixturePlcStatus.TESTING.value

    def is_pass(self) -> bool:
        return self.test_result == FixturePlcTestResult.PASS.value

    def is_failed(self) -> bool:
        return self.test_result == FixturePlcTestResult.FAILED.value

    def __str__(self):
        msg = ""
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "board_status":
                value = BoardPlcStatus.get_description(value)
            elif attribute == "test_result":
                value = FixturePlcTestResult.get_description(value)
            elif attribute == "fixture_status":
                value = FixturePlcStatus.get_description(value)
            msg += f"{attribute} = {value}\n"
        return msg
