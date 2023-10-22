from Core.Enums.TestStatus import TestStatus
from DataAccess.TestAnalyzer import TestAnalyzer
from Models.TestAnalysis import TestAnalysis
from Products.Mobo.MoboFctHostControlDAO import MoboFctHostControlDAO
from typing import Tuple
from Utils.TextNormalizer import normalizeToRegex
import os
import re
import subprocess


class MoboTestAnalyzer(TestAnalyzer):
    RUN_STATUS_FILE = "run_status"
    TEST_ITEM_FILE = "test_item"
    LOG_FILE = "run_test.log"
    BOARD_LOADED = "Check Status (TOTCCS): 2"
    BOARD_LOADED_REGEX = normalizeToRegex(BOARD_LOADED)
    BOARD_TESTING = "Start testing board"
    BOARD_TESTING_REGEX = normalizeToRegex(BOARD_TESTING)
    BOARD_RELEASED = "Check Status (TOTCCS): 4"
    BOARD_RELEASED_REGEX = normalizeToRegex(BOARD_RELEASED)

    def __init__(self, fixtureId: str, sessionId: str) -> None:
        super().__init__(sessionId)
        self._fixtureId = fixtureId
        self._serialNumber = ""
        self._currentLogFullpath = ""
        self.fctHostLogDataPath = (
            self._moboFctHostControlDAO.get_fct_host_log_data_fullpath(self._fixtureId)
        )
        self._moboFctHostControlDAO = MoboFctHostControlDAO()

    def can_recover(self) -> bool:
        return self._get_last_board_status() in [
            self.BOARD_LOADED,
            self.BOARD_TESTING,
            self.BOARD_RELEASED,
        ]

    def is_board_loaded(self) -> bool:
        return self._get_last_board_status() == self.BOARD_LOADED

    def _get_last_board_status(self) -> str:
        return subprocess.getoutput(
            f'tac "$(ls -1rt {self.fctHostLogDataPath}| tail -n1)" | grep -Poia -m1 "{self.BOARD_LOADED_REGEX}|{self.BOARD_TESTING_REGEX}|{self.BOARD_RELEASED_REGEX}'
        )

    def initialize_files(self) -> bool:
        # TODO
        return False

    def refresh_serial_number(self) -> str:
        # TODO
        self._serialNumber = self.buffer_extract("Serial Number\s*:\s*<*\K.*?(?=>)")[1]
        self._currentLogFullpath = (
            f"{self._moboFctHostControlDAO.get_script_out_path()}/{self._serialNumber}"
        )

    def is_testing(self) -> bool:
        # TODO
        return not self.is_finished() and self._is_popen_ok(
            f"cat {self._currentLogFullpath}/{self.TEST_ITEM_FILE} | sed '/^\\s*$/d' | wc -w | xargs test 0 -ne"
        )

    def _is_last_fixture_status_testing(self):
        return "Start testing board" in subprocess.getoutput(
            f"tail -n1 $(ls -1rt {self.fctHostLogDataPath} | tail -n1)"
        )

    def is_pretest_failed(self) -> str:
        # TODO
        return False

    def is_finished(self) -> bool:
        # TODO
        return self._is_popen_ok(
            f'cat {self._currentLogFullpath}/{self.RUN_STATUS_FILE} | grep -Poi "PASS|FAIL"'
        )

    def _is_popen_ok(self, cmd: str):
        popen = subprocess.Popen(cmd, stdout=None, shell=True)
        popen.communicate()
        return popen.returncode == 0

    def get_test_item(self) -> str:
        return subprocess.getoutput(
            f"cat {self._currentLogFullpath}/test_item | awk '{{print $1}}'"
        )

    def is_board_released(self) -> bool:
        return self._get_last_board_status() == self.BOARD_RELEASED

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
            serialNumber=self._serialNumber,
            stepLabel=stepLabel,
        )

    def _get_logfile(self):
        path = f"{self._moboFctHostControlDAO.get_script_out_path()}/{self._serialNumber}/{self.LOG_FILE}"
        if not os.path.isfile(path):
            return ""
        return path

    def _get_run_status(self) -> str:
        return subprocess.getoutput(
            f"cat {self._currentLogFullpath}/{self.RUN_STATUS_FILE} | awk '{{print $1}}'"
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
