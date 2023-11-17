from Widgets.PlcDataViewer.PlcStatus import PlcStatus


class NullPlcStatus(PlcStatus):
    def __init__(self) -> None:
        super().__init__()

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
