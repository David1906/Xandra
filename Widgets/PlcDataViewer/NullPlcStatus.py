from Widgets.PlcDataViewer.PlcStatus import PlcStatus


class NullPlcStatus(PlcStatus):
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

    def is_board_loaded(self) -> bool:
        return False

    def is_board_released(self) -> bool:
        return True

    def is_testing(self) -> bool:
        return False

    def is_pass(self) -> bool:
        return False

    def is_failed(self) -> bool:
        return False
