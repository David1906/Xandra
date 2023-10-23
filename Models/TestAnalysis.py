from __future__ import annotations
from Core.Enums.TestStatus import TestStatus
from datetime import datetime


class TestAnalysis:
    status = TestStatus.Initial
    stepLabel = ""
    logfile = ""
    serialNumber = ""
    startDateTime = None

    def __init__(
        self,
        status: TestStatus,
        logfile: str = "",
        stepLabel: str = "",
        serialNumber: str = "",
        startDateTime: datetime = None,
    ) -> None:
        self.status = status
        self.stepLabel = stepLabel
        self.logfile = logfile
        self.serialNumber = serialNumber
        self.startDateTime = startDateTime

    def is_testing(self) -> bool:
        return self.status == TestStatus.Tested

    def is_pass(self) -> bool:
        return self.status == TestStatus.Pass

    def equals(self, other: TestAnalysis) -> bool:
        return self.status == other.status and self.stepLabel == other.stepLabel

    def has_finished(self):
        return self.status in [
            TestStatus.Pass,
            TestStatus.Failed,
        ]
