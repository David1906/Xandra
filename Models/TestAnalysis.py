from __future__ import annotations
import re
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
        outLog: str = "",
        scriptVersion: str = "",
        bmcIp: str = "",
    ) -> None:
        self.status = status
        self.stepLabel = stepLabel
        self.logfile = logfile
        self.serialNumber = serialNumber
        self.startDateTime = startDateTime
        self.outLog = outLog
        self.scriptVersion = scriptVersion
        self.bmcIp = bmcIp

    def is_testing(self) -> bool:
        return self.status == TestStatus.Tested

    def is_pass(self) -> bool:
        return self.status == TestStatus.Pass

    def equals(self, other: TestAnalysis) -> bool:
        return (
            self.status == other.status
            and self.stepLabel == other.stepLabel
            and self.bmcIp == other.bmcIp
        )

    def has_finished(self):
        return self.status in [
            TestStatus.Pass,
            TestStatus.Failed,
        ]

    def is_l6_initial_error(self) -> bool:
        return self._step_label_contains("l6_initial_status")

    def _step_label_contains(self, regex: str) -> bool:
        match = re.search(regex, self.stepLabel, re.IGNORECASE)
        return match != None

    def get_out_log_path(self, fileName: str = ""):
        if fileName != "":
            return f"{self.outLog}/{fileName}"
        return self.outLog
