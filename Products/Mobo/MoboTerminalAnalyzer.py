from typing import Tuple
from Core.Enums.TerminalStatus import TerminalStatus
from Models.TerminalAnalysis import TerminalAnalysis
from DataAccess.TerminalAnalyzer import TerminalAnalyzer


class MoboTerminalAnalyzer(TerminalAnalyzer):
    def __init__(self, sessionId: str) -> None:
        super().__init__(sessionId)
        self.serialNumber = ""

    def calc_analysis(self) -> TerminalAnalysis:
        testStarted = self._get_test_started()
        testing = self._get_testing_item()
        testFinished = self._get_test_finished()
        currentStatus = self._get_latest([testStarted, testing, testFinished])

        analysis = TerminalAnalysis(TerminalStatus.IDLE)
        if currentStatus[0] == self.ERROR_ID:
            analysis = TerminalAnalysis(TerminalStatus.IDLE)
        elif currentStatus == testing or currentStatus == testStarted:
            if self.serialNumber == "":
                self.serialNumber = self._get_serial_number()[1]
            analysis = self._get_testing_analysis(testing)
        elif currentStatus == testFinished:
            analysis = self._get_test_finished_analysis(testing)
            self.serialNumber = ""
        return analysis

    def _get_testing_analysis(self, testing: Tuple[int, str]) -> TerminalAnalysis:
        return TerminalAnalysis(
            TerminalStatus.TESTING, serialNumber=self.serialNumber, stepLabel=testing[1]
        )

    def _get_test_finished_analysis(self, testing: Tuple[int, str]) -> TerminalAnalysis:
        outLog = self._get_logfile_path()
        logfile = outLog[1]
        if outLog[0] < testing[0]:
            logfile = ""
        serialNumber = (
            self.serialNumber if self.serialNumber != "" else self._get_serial_number()[1]
        )
        return TerminalAnalysis(
            self._get_pass_or_fail_status(), logfile, testing[1], serialNumber
        )

    def _get_pass_or_fail_status(self) -> TerminalStatus:
        passStatus = self._get_pass()
        failStatus = self._get_fail()
        latest = self._get_latest([passStatus, failStatus])
        return TerminalStatus.PASS if latest == passStatus else TerminalStatus.FAIL

    def _get_test_started(self) -> Tuple[int, str]:
        return self.buffer_extract("Fixture status is.*\(.*TAU_ready")

    def _get_test_finished(self) -> Tuple[int, str]:
        return self.buffer_extract("End Test")

    def _get_idle(self) -> Tuple[int, str]:
        return self.buffer_extract("Fixture\s*status\s*is|what.*\s*your\s*product")

    def _get_testing_item(self) -> Tuple[int, str]:
        return self.buffer_extract("Test_Item\s*:\s*\K.*|Power On Board")

    def _get_serial_number(self) -> Tuple[int, str]:
        return self.buffer_extract("Serial Number\s*:\s*<*\K.*?(?=>)")

    def _get_logfile_path(self):
        logRegex = "out log\s*:\s*"
        lineNo = self.buffer_extract(logRegex)
        path = self.buffer_extract(f"{logRegex}\K.*?\.log", multiline=True)
        return (lineNo[0], path[1])

    def _get_pass(self):
        return self.buffer_extract("Main testing PASS")

    def _get_fail(self):
        return self.buffer_extract("Main testing FAIL")

    def _get_latest(self, tuples: "list[Tuple[int,str]]") -> Tuple[int, str]:
        latest = tuples[0]
        for tuple in tuples:
            if latest[0] < tuple[0]:
                latest = tuple
        return latest
