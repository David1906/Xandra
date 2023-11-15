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

    def initialize_files(self):
        for file in [self._runStatusPath, self._testItemPath, self._startTimePath]:
            if os.path.isfile(file):
                open(file, "w").close()

    def refresh_board_data(self):
        self._serialNumber = self._get_plc_status().sn
        self._mac = self._get_plc_status().mac
        self._refresh_test_paths()
        self._call_get_bmc_ip()

    def _refresh_test_paths(self):
        self._currentLogPath = (
            f"{self._moboFctHostControlDAO.get_script_out_path()}/{self._serialNumber}"
        )
        self._runStatusPath = f"{self._currentLogPath}/{self.RUN_STATUS_FILE}"
        self._testItemPath = f"{self._currentLogPath}/{self.TEST_ITEM_FILE}"
        self._logFilePath = f"{self._currentLogPath}/{self.LOG_FILE}"
        self._startTimePath = f"{self._currentLogPath}/{self.START_TIME_FILE}"
        self._bmcIpPath = f"{self._currentLogPath}/{self.BMC_IP_FILE}"

    def _call_get_bmc_ip(self):
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

    def get_start_time(self) -> datetime:
        # TODO Optimizar lectura de archivo
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
        return self._run_status_match("testing")

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
        return not self._get_plc_status().is_testing() or self._run_status_match(
            "PASS|FAILED"
        )

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

    def get_test_analysis(
        self, testStatus: TestStatus, stepLabel: str = None
    ) -> TestAnalysis:
        # TODO optimizar lectura de datos
        testAnalysis = TestAnalysis(
            status=testStatus,
            serialNumber=self._serialNumber,
            stepLabel=stepLabel if stepLabel != None else self.get_test_item(),
            startDateTime=self.get_start_time(),
            outLog=self._currentLogPath,
        )
        if testStatus.is_testing():
            testAnalysis.bmcIp = self.get_bmc_ip()
        elif testStatus.is_ended():
            testAnalysis.logfile = self._get_logfile()
            testAnalysis.scriptVersion = (
                self._moboFctHostControlDAO.get_script_version()
            )
        return testAnalysis

    def _get_logfile(self):
        if not os.path.isfile(self._logFilePath):
            return ""
        return self._logFilePath

    def get_fixture_ip(self) -> str:
        return self._fixture.ip
