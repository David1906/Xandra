from __future__ import annotations
from Core.Enums.TerminalStatus import TerminalStatus


class TerminalAnalysis:
    status = TerminalStatus.UNKNOWN
    stepLabel = ""
    logfile = ""
    serialNumber = ""

    def __init__(
        self,
        status: TerminalStatus,
        logfile: str = "",
        stepLabel: str = "",
        serialNumber: str = "",
    ) -> None:
        self.status = status
        self.stepLabel = stepLabel
        self.logfile = logfile
        self.serialNumber = serialNumber

    def is_testing(self) -> bool:
        return self.status == TerminalStatus.TESTING

    def is_pass(self) -> bool:
        return self.status == TerminalStatus.PASS

    def equals(self, other: TerminalAnalysis) -> bool:
        return self.status == other.status and self.stepLabel == other.stepLabel
