from PlcAddress import PlcAdress


class PlcStatus:
    def __init__(self) -> None:
        self.mac = ""
        self.sn = ""
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

    def set_data(self, rawData: "list(int)"):
        self.mac = self._raw_data_to_str(rawData, PlcAdress.ADDR_MAC, PlcAdress.MAC_LEN)
        self.sn = self._raw_data_to_str(rawData, PlcAdress.ADDR_SN, PlcAdress.SN_LEN)
        self.device_no = self._extract_single_address(rawData, PlcAdress.ADDR_DEVICE_NO)
        self.mode = self._extract_single_address(rawData, PlcAdress.ADDR_MODE)
        self.heartbeat = self._extract_single_address(rawData, PlcAdress.ADDR_HEARTBEAT)
        self.test_no = self._extract_single_address(rawData, PlcAdress.ADDR_TEST_NO)
        self.test_result = self._extract_single_address(
            rawData, PlcAdress.ADDR_TEST_RESULT
        )
        self.request_mode = self._extract_single_address(
            rawData, PlcAdress.ADDR_REQUEST_MODE
        )
        self.return_mode = self._extract_single_address(
            rawData, PlcAdress.ADDR_RETURN_MODE
        )
        self.send_in_out_enable = self._extract_single_address(
            rawData, PlcAdress.ADDR_SEND_IN_OUT_ENABLE
        )
        self.fixture_status = self._extract_single_address(
            rawData, PlcAdress.ADDR_FIXTURE_STATUS
        )
        self.lifter = self._extract_single_address(rawData, PlcAdress.ADDR_LIFTER)
        self.scan = self._extract_single_address(rawData, PlcAdress.ADDR_SCAN)
        self.fixture_error = self._extract_single_address(
            rawData, PlcAdress.ADDR_FIXTURE_ERROR
        )
        self.tccs_task_no = self._raw_data_to_str(
            rawData, PlcAdress.ADDR_TCCS_TASK_NO, PlcAdress.TCCS_TASK_NO_LEN
        )
        self.model_id = self._raw_data_to_str(
            rawData, PlcAdress.ADDR_MODEL_ID, PlcAdress.MODEL_ID_LEN
        )
        self.fixture_id = self._raw_data_to_str(
            rawData, PlcAdress.ADDR_FIXTURE_ID, PlcAdress.FIXTURE_ID_LEN
        )

    def _raw_data_to_str(
        self, rawData: "list(int)", startAddr: int, len: int = 1
    ) -> str:
        chunk = self._extract_chunk(rawData, startAddr, len)
        asciiChunk = list(filter(lambda x: x != 0, chunk))
        string = "".join(self._ascii_to_char(asciiChunk))
        return "Empty" if string == "" else string

    def _extract_single_address(self, rawData: "list(int)", startAddr: int) -> int:
        return self._extract_chunk(rawData, startAddr)[0]

    def _extract_chunk(
        self, rawData: "list(int)", startAddr: int, len: int = 1
    ) -> "list(int)":
        start = startAddr - PlcAdress.STARTADDR
        return rawData[start : start + len]

    def _ascii_to_char(self, ascii: "list(int)"):
        return [chr(character) for character in ascii]
