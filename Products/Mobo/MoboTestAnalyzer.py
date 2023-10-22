from Core.Enums.TestStatus import TestStatus
from DataAccess.TestAnalyzer import TestAnalyzer
from Models.TestAnalysis import TestAnalysis
from Products.Mobo.MoboFctHostControlDAO import MoboFctHostControlDAO
from typing import Tuple
import os
import re
import subprocess


class MoboTestAnalyzer(TestAnalyzer):
    RUN_STATUS_FILE = "run_status"
    TEST_ITEM_FILE = "test_item"
    LOG_FILE = "run_test.log"

    def __init__(self, sessionId: str) -> None:
        super().__init__(sessionId)
        self.serialNumber = ""
        self.lastNonSFCTest = ""
        self.currentLogFullpath = ""
        self._moboFctHostControlDAO = MoboFctHostControlDAO()

    def can_recover(self) -> bool:
        # TODO
        # Extraer de archivo de fcthost control Start testing board == (tail -n 1)
        return False

    def is_board_loaded(self) -> bool:
        # TODO
        return False

    def initialize_files(self) -> bool:
        # TODO
        return False

    def refresh_serial_number(self) -> str:
        self.serialNumber = self.buffer_extract("Serial Number\s*:\s*<*\K.*?(?=>)")[1]
        self.currentLogFullpath = (
            f"{self._moboFctHostControlDAO.get_script_out_path()}/{self.serialNumber}"
        )

    def is_testing(self) -> bool:
        # TODO
        return not self.is_finished() and self._is_popen_ok(
            f"cat {self.currentLogFullpath}/{self.TEST_ITEM_FILE} | sed '/^\\s*$/d' | wc -w | xargs test 0 -ne"
        )

    def is_pretest_failed(self) -> str:
        # TODO
        return False

    def is_finished(self) -> bool:
        # TODO
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

    def is_board_released(self) -> bool:
        # TODO
        return False

    def is_pass(self) -> TestAnalysis:
        # TODO
        return False

    def is_failed(self) -> TestAnalysis:
        # TODO
        return False

    def get_released_test_analysis(self) -> TestAnalysis:
        # TODO
        terminalStatus = TestStatus.Pass
        stepLabel = ""
        if re.match(".*FAIL.*", self._get_run_status()):
            terminalStatus = TestStatus.Failed
            stepLabel = self.get_test_item()
        return TestAnalysis(
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
        return self.buffer_extract(".*Checking.*SN.*MAC.*")

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
