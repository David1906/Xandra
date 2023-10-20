import os
import re
import subprocess
from typing import Tuple
from Core.Enums.TerminalStatus import TerminalStatus
from Models.TerminalAnalysis import TerminalAnalysis
from DataAccess.TerminalAnalyzer import TerminalAnalyzer
from Products.Mobo.MoboFctHostControlDAO import MoboFctHostControlDAO


class MoboTerminalAnalyzer(TerminalAnalyzer):
    RUN_STATUS_FILE = "run_status"
    TEST_ITEM_FILE = "test_item"
    LOG_FILE = "run_test.log"

    def __init__(self, sessionId: str) -> None:
        super().__init__(sessionId)
        self.serialNumber = ""
        self.lastNonSFCTest = ""
        self.currentLogFullpath = ""
        self._moboFctHostControlDAO = MoboFctHostControlDAO()

    def is_board_loaded(self) -> bool:
        testStarted = self._get_test_started()
        testFinished = self._get_test_finished()
        latest = self._get_latest([testStarted, testFinished])
        return testStarted[0] != self.ERROR_ID and testStarted == latest

    def initialize_files(self) -> str:
        subprocess.Popen(
            f'echo "" > {self.currentLogFullpath}/{self.RUN_STATUS_FILE}',
            stdout=None,
            shell=True,
        )

    def is_power_on(self) -> bool:
        testStarted = self._get_test_started()
        testPowered = self._get_test_powered_on()
        testFinished = self._get_test_finished()
        latest = self._get_latest([testStarted, testPowered, testFinished])
        return testPowered[0] != self.ERROR_ID and testPowered == latest

    def refresh_serial_number(self) -> Tuple[int, str]:
        self.serialNumber = self.buffer_extract("Serial Number\s*:\s*<*\K.*?(?=>)")[1]
        self.currentLogFullpath = (
            f"{self._moboFctHostControlDAO.get_script_out_path()}/{self.serialNumber}"
        )

    def is_testing(self) -> bool:
        return not self.is_finished() and self._is_popen_ok(
            f"cat {self.currentLogFullpath}/{self.TEST_ITEM_FILE} | sed '/^\\s*$/d' | wc -w | xargs test 0 -ne"
        )

    def is_finished(self) -> bool:
        return self._is_popen_ok(
            f'cat {self.currentLogFullpath}/{self.RUN_STATUS_FILE} | grep -Poi "PASS|FAIL"'
        )

    def _is_popen_ok(self, cmd: str):
        popen = subprocess.Popen(cmd, stdout=None, shell=True)
        popen.communicate()
        return popen.returncode == 0

    def get_test_item(self) -> str:
        return subprocess.getoutput(
            f"cat {self.currentLogFullpath}/test_item | awk '{{print $1}}'"
        )

    def get_finished_terminalAnalysis(self) -> TerminalAnalysis:
        terminalStatus = TerminalStatus.PASS
        stepLabel = ""
        if re.match(".*FAIL.*", self._get_run_status()):
            terminalStatus = TerminalStatus.FAIL
            stepLabel = self.get_test_item()
        return TerminalAnalysis(
            terminalStatus,
            logfile=self._get_logfile(),
            serialNumber=self.serialNumber,
            stepLabel=stepLabel,
        )

    def _get_logfile(self):
        path = f"{self._moboFctHostControlDAO.get_script_out_path()}/{self.serialNumber}/{self.LOG_FILE}"
        if not os.path.isfile(path):
            return ""
        return path

    def _get_run_status(self) -> str:
        return subprocess.getoutput(
            f"cat {self.currentLogFullpath}/{self.RUN_STATUS_FILE} | awk '{{print $1}}'"
        )

    def is_stopped(self) -> bool:
        popen = subprocess.Popen(
            f"tmux has-session -t {self.sessionId}", stdout=None, shell=True
        )
        popen.communicate()
        return popen.returncode != 0

    def _get_test_started(self) -> Tuple[int, str]:
        return self.buffer_extract("Fixture status is.*\(.*UUT_powering")

    def _get_test_powered_on(self) -> Tuple[int, str]:
        return self.buffer_extract("Fixture status is.*\(.*UUT_powered")

    def _get_test_finished(self) -> Tuple[int, str]:
        return self.buffer_extract("─────────── End Test ───────────")

    def _get_latest(self, tuples: "list[Tuple[int,str]]") -> Tuple[int, str]:
        latest = tuples[0]
        for tuple in tuples:
            if latest[0] < tuple[0]:
                latest = tuple
        return latest
