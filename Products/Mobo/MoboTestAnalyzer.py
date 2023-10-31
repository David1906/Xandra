from Core.Enums.TestStatus import TestStatus
from DataAccess.TestAnalyzer import TestAnalyzer
from datetime import datetime
from Models.TestAnalysis import TestAnalysis
from Products.Mobo.MoboFctHostControlDAO import MoboFctHostControlDAO
from Utils.TextNormalizer import normalizeToRegex
import os
import re
import subprocess


class MoboTestAnalyzer(TestAnalyzer):
    START_TIME_FILE = "starttime"
    RUN_STATUS_FILE = "run_status"
    TEST_ITEM_FILE = "test_item"
    LOG_FILE = "run_test.log"
    BOARD_LOADED = "Get SN:"
    BOARD_LOADED_REGEX = normalizeToRegex(BOARD_LOADED)
    BOARD_TESTING = "Start testing board"
    BOARD_TESTING_REGEX = normalizeToRegex(BOARD_TESTING)
    BOARD_RELEASED = "Check Status (ToTCCS): 4"
    BOARD_RELEASED_REGEX = normalizeToRegex(BOARD_RELEASED)
    BOARD_SOCKET_EXCEPTIONS = "ERROR"
    BOARD_SOCKET_EXCEPTIONS_REGEX = normalizeToRegex(BOARD_SOCKET_EXCEPTIONS)
    BOARD_TEST_INITIALIZING = "Testing initializing"
    BOARD_TEST_INITIALIZING_REGEX = normalizeToRegex(BOARD_TEST_INITIALIZING)

    def __init__(self, fixtureId: str, sessionId: str) -> None:
        super().__init__(sessionId)
        self._fixtureId = fixtureId
        self._serialNumber = ""
        self._currentLogPath = ""
        self._runStatusPath = ""
        self._testItemPath = ""
        self._logFilePath = ""
        self._startTimePath = ""
        self._moboFctHostControlDAO = MoboFctHostControlDAO()
        self.fctHostLogDataPath = (
            self._moboFctHostControlDAO.get_fct_host_log_data_fullpath(self._fixtureId)
        )

    def can_recover(self) -> bool:
        self._debug_thread()
        return self._get_last_board_status() in [
            self.BOARD_LOADED,
            self.BOARD_TESTING,
        ]

    def _debug_thread(self, sessionId: str = "console_1"):
        if os.environ.get("ENV") == "testing" and self.sessionId == sessionId:
            import debugpy

            debugpy.debug_this_thread()

    def is_board_loaded(self) -> bool:
        return self._get_last_board_status() == self.BOARD_LOADED

    def _get_last_board_status(
        self, tail: int = 100, includeInitializing: bool = False
    ) -> str:
        regex = f"{self.BOARD_LOADED_REGEX}|{self.BOARD_TESTING_REGEX}|{self.BOARD_RELEASED_REGEX}|{self.BOARD_SOCKET_EXCEPTIONS_REGEX}"
        if includeInitializing:
            regex += f"|{self.BOARD_TEST_INITIALIZING_REGEX}"
        return (
            subprocess.getoutput(
                f'tail -n{tail} {self.fctHostLogDataPath}/"$(ls -1rt {self.fctHostLogDataPath}| tail -n1)" | tac | grep -Poia -m1 "{regex}"'
            )
            .strip()
            .split("\n")[0]
        )

    def initialize_files(self):
        open(self._runStatusPath, "w").close()
        open(self._startTimePath, "w").close()
        open(self._testItemPath, "w").close()

    def refresh_serial_number(self):
        self._serialNumber = subprocess.getoutput(
            f'tac {self.fctHostLogDataPath}/"$(ls -1rt {self.fctHostLogDataPath}| tail -n1)" | grep -Poia -m1 "Get SN\s*:\s*\K.*?(?=\|)" | tail -n1'
        ).strip()

    def refresh_test_paths(self):
        self._currentLogPath = (
            f"{self._moboFctHostControlDAO.get_script_out_path()}/{self._serialNumber}"
        )
        self._runStatusPath = f"{self._currentLogPath}/{self.RUN_STATUS_FILE}"
        self._testItemPath = f"{self._currentLogPath}/{self.TEST_ITEM_FILE}"
        self._logFilePath = f"{self._currentLogPath}/{self.LOG_FILE}"
        self._startTimePath = f"{self._currentLogPath}/{self.START_TIME_FILE}"

    def get_start_time(self) -> datetime:
        startTime = subprocess.getoutput(
            f"cat {self._startTimePath} | awk '{{print $1}}'",
        )
        dt = datetime.now()
        try:
            dt = datetime.strptime(startTime, "%Y%m%d_%H%M%S")
        except:
            pass
        return dt

    def is_testing(self) -> bool:
        return self._get_last_board_status(tail=1) == self.BOARD_TESTING

    def is_finished(self) -> bool:
        return self._is_popen_ok(f'cat "{self._runStatusPath}" | grep -Poi "PASS|FAIL"')

    def _is_popen_ok(self, cmd: str):
        popen = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
        )
        popen.communicate()
        return popen.returncode == 0

    def get_test_item(self) -> str:
        if not os.path.isfile(self._testItemPath):
            return ""
        return subprocess.getoutput(
            f"cat {self._testItemPath} | awk '{{print $1}}'",
        )

    def is_board_released(self) -> bool:
        self._debug_thread()
        return self._get_last_board_status(includeInitializing=True) in [
            self.BOARD_RELEASED,
            self.BOARD_SOCKET_EXCEPTIONS,
            self.BOARD_TEST_INITIALIZING,
        ]

    def is_pass(self) -> bool:
        return re.match("PASS", self._get_run_status_text(), re.IGNORECASE) != None

    def is_failed(self) -> bool:
        return re.match("FAILED", self._get_run_status_text(), re.IGNORECASE) != None

    def _get_run_status_text(self) -> str:
        return subprocess.getoutput(f"cat {self._runStatusPath} | awk '{{print $1}}'")

    def get_pass_test_analysis(self) -> TestAnalysis:
        return TestAnalysis(
            TestStatus.Pass,
            logfile=self._get_logfile(),
            serialNumber=self._serialNumber,
        )

    def get_failed_test_analysis(self) -> TestAnalysis:
        return TestAnalysis(
            status=TestStatus.Failed,
            logfile=self._get_logfile(),
            serialNumber=self._serialNumber,
            stepLabel=self.get_test_item(),
        )

    def _get_logfile(self):
        if not os.path.isfile(self._logFilePath):
            return ""
        return self._logFilePath
