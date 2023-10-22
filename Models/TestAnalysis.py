from __future__ import annotations
from Core.Enums.TestStatus import TestStatus


class TestAnalysis:
    status = TestStatus.Initial
    stepLabel = ""
    logfile = ""
    serialNumber = ""

    def __init__(
        self,
        status: TestStatus,
        logfile: str = "",
        stepLabel: str = "",
        serialNumber: str = "",
    ) -> None:
        self.status = status
        self.stepLabel = stepLabel
        self.logfile = logfile
        self.serialNumber = serialNumber

    def is_testing(self) -> bool:
        return self.status == TestStatus.Tested

    def is_pass(self) -> bool:
        return self.status == TestStatus.Pass

    def equals(self, other: TestAnalysis) -> bool:
        return self.status == other.status and self.stepLabel == other.stepLabel
