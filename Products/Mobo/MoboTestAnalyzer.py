import re
from Core.Enums.TestEvent import TestEvent
from Core.Enums.TestStatus import TestStatus
from DataAccess.TestAnalyzer import TestAnalyzer
from datetime import datetime
from Models.Fixture import Fixture
from Models.TestAnalysis import TestAnalysis
from Products.Mobo.MoboFctHostControlDAO import MoboFctHostControlDAO
from Utils.PathHelper import PathHelper
from Widgets.PlcDataViewer.NullPlcStatus import NullPlcStatus
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
        super().__init__(fixture, sessionId)
        self._serialNumber = ""
        self._mac = ""
        self._bmcIp = ""
        self._startTime = None
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
        self._lastPlcStatus: PlcStatus = NullPlcStatus()
        self._lastTestStatus = ""

    def is_changed(self) -> bool:
        plcStatus = self._get_plc_status()
        if (
            not self._lastPlcStatus.equals_statuses(plcStatus)
            or self.is_test_status_changed()
        ):
            self._lastPlcStatus = plcStatus
            return True
        return False

    def is_test_status_changed(self):
        testStatus = (
            self._get_run_status_text() + self._get_test_item() + self._get_bmc_ip()
        )
        if testStatus != self._lastTestStatus:
            self._lastTestStatus = testStatus
            return True
        return False

    def get_event(self) -> TestEvent:
        event = None
        if self._stateMachine.can_test() and self.is_testing():
            event = TestEvent.Test
        elif self._stateMachine.can_load_board() and self.is_board_loaded():
            event = TestEvent.LoadBoard
        elif self._stateMachine.can_finish() and self.is_finished():
            event = TestEvent.Finish
        elif self._stateMachine.can_idle() and self.is_board_released():
            event = TestEvent.Release
        elif self._stateMachine.is_initialized():
            event = TestEvent.Idle
        return event

    def is_board_loaded(self) -> bool:
        return self._get_plc_status().is_board_loaded()

    def is_testing(self) -> bool:
        return self._run_status_match("testing") and self._get_plc_status().is_testing()

    def is_finished(self) -> bool:
        return self._is_pass() or self._is_failed()

    def is_board_released(self) -> bool:
        return self._get_plc_status().is_board_released()

    def _get_plc_status(self) -> PlcStatus:
        return self._plcDAO.get_status_debounced()

    def initialize_test(self):
        self._initialize_files()
        self._refresh_board_data()
        self._call_get_bmc_ip()
        print(
            f"Initialize Test {self._sessionId}: sn:{self._serialNumber} mac: {self._mac} bmcIp:{self._bmcIp}"
        )

    def _initialize_files(self):
        for file in [self._runStatusPath, self._testItemPath, self._startTimePath]:
            if os.path.isfile(file):
                open(file, "w").close()

    def _refresh_board_data(self):
        self._serialNumber = self._get_plc_status().sn
        self._mac = self._get_plc_status().mac
        self._startTime = None
        self._bmcIp = None
        self._refresh_test_paths()

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

    def _run_status_match(self, text: str) -> bool:
        return re.match(text, self._get_run_status_text(), re.IGNORECASE) != None

    def _get_run_status_text(self) -> str:
        if not os.path.isfile(self._runStatusPath):
            return ""
        try:
            return subprocess.getoutput(
                f"cat {self._runStatusPath} | awk '{{print $1}}'"
            )
        except:
            return ""

    def get_test_analysis(
        self, testStatus: TestStatus, stepLabel: str = None
    ) -> TestAnalysis:
        testAnalysis = TestAnalysis(
            status=testStatus,
            serialNumber=self._serialNumber,
            mac=self._mac,
            stepLabel=stepLabel if stepLabel != None else self._get_test_item(),
            startDateTime=self._get_start_time(),
            outLog=self._currentLogPath,
        )
        if testStatus in [TestStatus.BoardLoaded, TestStatus.Tested]:
            testAnalysis.bmcIp = self._get_bmc_ip()
        elif testStatus == TestStatus.Finished:
            testAnalysis.result = self._get_test_result()
            testAnalysis.logfile = self._get_logfile()
            testAnalysis.scriptVersion = (
                self._moboFctHostControlDAO.get_script_version()
            )
        return testAnalysis

    def _get_test_item(self) -> str:
        if not os.path.isfile(self._testItemPath):
            return ""
        try:
            return subprocess.getoutput(
                f"cat {self._testItemPath} | awk '{{print $1}}'",
            )
        except:
            return ""

    def _get_start_time(self) -> datetime:
        if self._startTime != None:
            return self._startTime
        try:
            startTime = subprocess.getoutput(
                f"timeout 1s cat {self._startTimePath} | awk '{{print $1}}'",
            )
            self._startTime = datetime.strptime(startTime, "%Y%m%d_%H%M%S")
        except:
            self._startTime = datetime.now()
        return self._startTime

    def _get_bmc_ip(self) -> str:
        if self._bmcIp != None and self._bmcIp != "":
            return self._bmcIp
        try:
            if os.path.isfile(self._bmcIpPath):
                self._bmcIp = subprocess.getoutput(
                    f"cat {self._bmcIpPath} | tail -1",
                ).strip()
            else:
                self._bmcIp = ""
        except:
            self._bmcIp = ""
        if self._bmcIp != None and self._bmcIp != "":
            print(f"{self._sessionId} bmcIp detected: {self._bmcIp}")
        return self._bmcIp

    def _get_test_result(self):
        if self._is_pass():
            return True
        elif self._is_failed():
            return False
        return None

    def _is_pass(self) -> bool:
        return self._get_plc_status().is_pass() or self._run_status_match("PASS")

    def _is_failed(self) -> bool:
        return self._get_plc_status().is_failed() or self._run_status_match("FAILED")

    def _get_logfile(self):
        if not os.path.isfile(self._logFilePath):
            return ""
        return self._logFilePath
