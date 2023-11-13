import re
from Core.Enums.TestStatus import TestStatus
from DataAccess.TestAnalyzer import TestAnalyzer
from datetime import datetime
from Models.Fixture import Fixture
from Models.TestAnalysis import TestAnalysis
from Products.Mobo.MoboFctHostControlDAO import MoboFctHostControlDAO
from Utils.PathHelper import PathHelper
from Utils.TextNormalizer import normalizeToRegex
from Widgets.PlcDataViewer.PlcDAO import PlcDAO
from Widgets.PlcDataViewer.PlcStatus import PlcStatus
import os
import subprocess


class MoboTestAnalyzer(TestAnalyzer):
    START_TIME_FILE = "starttime"
    RUN_STATUS_FILE = "run_status"
    TEST_ITEM_FILE = "test_item"
    LOG_FILE = "run_test.log"
    BMC_IP_FILE = "bmcip.txt"
    BOARD_LOADED = "Get SN:"
    BOARD_LOADED_REGEX = normalizeToRegex(BOARD_LOADED)
    BOARD_TESTING = "Start testing board"
    BOARD_TESTING_REGEX = normalizeToRegex(BOARD_TESTING)
    BOARD_RELEASED = "Check Status (ToTCCS): 4"
    BOARD_RELEASED_REGEX = normalizeToRegex(BOARD_RELEASED)
    BOARD_SOCKET_EXCEPTIONS = "ERROR"
    BOARD_SOCKET_EXCEPTIONS_REGEX = normalizeToRegex(BOARD_SOCKET_EXCEPTIONS)
    RUN_TEST_FAILED = "Testing board FAIL"
    RUN_TEST_FAILED_REGEX = normalizeToRegex(RUN_TEST_FAILED)
    RUN_TEST_PASS = "Testing board PASS"
    RUN_TEST_PASS_REGEX = normalizeToRegex(RUN_TEST_PASS)

    def __init__(self, fixture: Fixture, sessionId: str) -> None:
        super().__init__(sessionId)
        self._fixture = fixture
        self._serialNumber = ""
        self._mac = ""
        self._currentLogPath = ""
        self._runStatusPath = ""
        self._testItemPath = ""
        self._logFilePath = ""
        self._startTimePath = ""
        self._bmcIpPath = ""
        self._moboFctHostControlDAO = MoboFctHostControlDAO()
        self._fctHostLogDataPath = (
            self._moboFctHostControlDAO.get_fct_host_log_data_fullpath(self._fixture.id)
        )
        self._plcDAO = PlcDAO(fixture.ip, fixture.port)

    def can_recover(self) -> bool:
        self._debug_thread()
        return self._get_plc_status().is_board_loaded()

    def _debug_thread(self, sessionId: str = "console_1"):
        if os.environ.get("ENV") == "testing" and self.sessionId == sessionId:
            import debugpy

            debugpy.debug_this_thread()

    def _get_plc_status(self) -> PlcStatus:
        return self._plcDAO.get_status_debounced()

    def is_board_loaded(self) -> bool:
        return self._get_plc_status().is_board_loaded()

    def _get_last_board_result(self):
        regex = f"{self.BOARD_LOADED_REGEX}|{self.RUN_TEST_PASS_REGEX}|{self.RUN_TEST_FAILED_REGEX}"
        return self._get_last_fixture_status(regex)

    def _get_last_board_status(self, tail: int = 100) -> str:
        regex = f"{self.BOARD_LOADED_REGEX}|{self.BOARD_TESTING_REGEX}"
        regex += f"|{self.RUN_TEST_PASS_REGEX}|{self.RUN_TEST_FAILED_REGEX}"
        regex += f"|{self.BOARD_RELEASED_REGEX}|{self.BOARD_SOCKET_EXCEPTIONS_REGEX}"
        return self._get_last_fixture_status(regex, tail)

    def _get_last_fixture_status(self, regex: str, tail: int = 100) -> str:
        try:
            return (
                subprocess.getoutput(
                    f'tail -n{tail} {self._fctHostLogDataPath}/"$(ls -1rt {self._fctHostLogDataPath}| tail -n1)" | tac | grep -Poia -m1 "{regex}"'
                )
                .strip()
                .split("\n")[0]
            )
        except:
            return ""

    def initialize_files(self):
        open(self._runStatusPath, "w").close()
        open(self._testItemPath, "w").close()

    def refresh_serial_number(self):
        self._serialNumber = self._get_plc_status().sn

    def refresh_mac(self):
        self._mac = self._get_plc_status().mac

    def refresh_test_paths(self):
        self._currentLogPath = (
            f"{self._moboFctHostControlDAO.get_script_out_path()}/{self._serialNumber}"
        )
        self._runStatusPath = f"{self._currentLogPath}/{self.RUN_STATUS_FILE}"
        self._testItemPath = f"{self._currentLogPath}/{self.TEST_ITEM_FILE}"
        self._logFilePath = f"{self._currentLogPath}/{self.LOG_FILE}"
        self._startTimePath = f"{self._currentLogPath}/{self.START_TIME_FILE}"
        self._bmcIpPath = f"{self._currentLogPath}/{self.BMC_IP_FILE}"

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
        return self._is_popen_ok(f'cat "{self._runStatusPath}" | grep -Poi "testing"')

    def call_get_bmc_ip(self):
        try:
            subprocess.Popen(
                f"{PathHelper().get_root_path()}/Resources/mobo/get_bmcip_onlyip.sh -s {self._serialNumber}",
                stdin=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
                cwd=self._moboFctHostControlDAO.get_script_fullpath(),
            )
        except:
            pass

    def get_bmc_ip(self) -> str:
        if not os.path.isfile(self._bmcIpPath):
            return ""
        try:
            return subprocess.getoutput(
                f"cat {self._bmcIpPath} | tail -1",
            ).strip()
        except:
            return ""

    def is_finished(self) -> bool:
        return not self._get_plc_status().is_testing() or self._run_status_match("PASS|FAILED")

    def _is_popen_ok(self, cmd: str):
        try:
            subprocess.check_call(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
            )
            return True
        except:
            return False

    def get_test_item(self) -> str:
        if not os.path.isfile(self._testItemPath):
            return ""
        try:
            return subprocess.getoutput(
                f"cat {self._testItemPath} | awk '{{print $1}}'",
            )
        except:
            return ""

    def is_board_released(self) -> bool:
        return self._get_plc_status().is_board_released()

    def is_pass(self) -> bool:
        return self._get_plc_status().is_pass() or self._run_status_match("PASS")

    def is_failed(self) -> bool:
        return self._get_plc_status().is_failed() or self._run_status_match("FAILED")

    def _run_status_match(self, text: str) -> bool:
        return re.match(text, self._get_run_status_text(), re.IGNORECASE) != None

    def _get_run_status_text(self) -> str:
        try:
            return subprocess.getoutput(
                f"cat {self._runStatusPath} | awk '{{print $1}}'"
            )
        except:
            return ""

    def get_pass_test_analysis(self) -> TestAnalysis:
        return TestAnalysis(
            TestStatus.Pass,
            logfile=self._get_logfile(),
            serialNumber=self._serialNumber,
            startDateTime=self.get_start_time(),
            outLog=self._currentLogPath,
            scriptVersion=self._moboFctHostControlDAO.get_script_version(),
        )

    def get_failed_test_analysis(self) -> TestAnalysis:
        return TestAnalysis(
            status=TestStatus.Failed,
            logfile=self._get_logfile(),
            serialNumber=self._serialNumber,
            stepLabel=self.get_test_item(),
            startDateTime=self.get_start_time(),
            outLog=self._currentLogPath,
            scriptVersion=self._moboFctHostControlDAO.get_script_version(),
        )

    def _get_logfile(self):
        if not os.path.isfile(self._logFilePath):
            return ""
        return self._logFilePath

    def pause(self):
        subprocess.Popen(
            f'echo "{datetime.today()}|ERROR|Xandra terminal stopped|" >> {self._fctHostLogDataPath}/"$(ls -1rt {self._fctHostLogDataPath}| tail -n1)"',
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )

    def get_serial_number(self) -> str:
        return self._serialNumber

    def get_mac(self) -> str:
        return self._mac

    def get_fixture_ip(self) -> str:
        return self._fixture.ip
