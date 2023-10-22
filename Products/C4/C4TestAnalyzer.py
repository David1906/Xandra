from typing import Tuple
from Core.Enums.TestStatus import TestStatus
from Models.TestAnalysis import TestAnalysis
from DataAccess.TestAnalyzer import TestAnalyzer


class C4TestAnalyzer(TestAnalyzer):
    def __init__(self, sessionId: str) -> None:
        super().__init__(sessionId)
        self.serialNumber = ""

    def calc_analysis(self) -> TestAnalysis:
        testing = self._get_testing_item()
        finished = self._get_test_finished()
        latest = self._get_latest([testing, finished])
        analysis = TestAnalysis(TestStatus.IDLE)
        if latest == testing:
            serialNumber = self._get_serial_number()
            if serialNumber[1] != "":
                self.serialNumber = serialNumber[1]
            analysis = TestAnalysis(TestStatus.TESTING, stepLabel=testing[1])
        elif latest == finished:
            outLog = self._get_logfile_path()
            logfile = outLog[1]
            if outLog[0] < testing[0]:
                logfile = ""
            analysis = TestAnalysis(
                self._get_pass_or_fail_status(), logfile, testing[1], self.serialNumber
            )
            self.serialNumber = ""
        return analysis

    def _get_pass_or_fail_status(self) -> TestStatus:
        passStatus = self._get_pass()
        failStatus = self._get_fail()
        latest = self._get_latest([passStatus, failStatus])
        return TestStatus.PASS if latest == passStatus else TestStatus.FAIL

    def _get_test_finished(self) -> Tuple[int, str]:
        return self.buffer_extract("Total Duration\s*:\s*\K.*")

    def _get_testing_item(self) -> Tuple[int, str]:
        return self.buffer_extract("Test_Item\s*:\s*\K.*")

    def _get_serial_number(self) -> Tuple[int, str]:
        return self.buffer_extract("SN\s*:\s*\K.*")

    def _get_logfile_path(self):
        logRegex = "out log\s*:\s*"
        lineNo = self.buffer_extract(logRegex)
        path = self.buffer_extract(f"{logRegex}\K.*?\.log", multiline=True)
        return (lineNo[0], path[1])

    def _get_pass(self):
        return self.buffer_extract(".*XX    XX  XX    XX  XX     X  XX     X.*")

    def _get_fail(self):
        return self.buffer_extract(".*XX        XX    XX     XX     XXX.*")

    def _get_latest(self, tuples: "list[Tuple[int,str]]") -> Tuple[int, str]:
        latest = tuples[0]
        for tuple in tuples:
            if latest[0] < tuple[0]:
                latest = tuple
        return latest
