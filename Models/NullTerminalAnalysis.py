from Core.Enums.TerminalStatus import TerminalStatus
from Models.TerminalAnalysis import TerminalAnalysis


class NullTerminalAnalysis(TerminalAnalysis):
    def __init__(self) -> None:
        super().__init__(TerminalStatus.UNKNOWN, stepLabel="")
