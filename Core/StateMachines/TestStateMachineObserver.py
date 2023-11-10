from datetime import datetime
from Core.Enums.TestStatus import TestStatus
from DataAccess.TestAnalyzer import TestAnalyzer
from Models.TestAnalysis import TestAnalysis
from Products.TestAnalyzerBuilder import TestAnalyzerBuilder
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from statemachine import State
import os


class TestStateMachineObserver(QtCore.QObject):
    update = QtCore.pyqtSignal(TestAnalysis)

    def __init__(
        self,
        parent: QObject,
        testAnalyzer: TestAnalyzer,
    ) -> None:
        super().__init__(parent)
        self._testAnalyzer = testAnalyzer
        self._isTransition = False

    def before_cycle(self, event: str, source: State, target: State, message: str = ""):
        self._isTransition = source.id != target.id
        if self._isTransition:
            self._log_transition(source, target)

    def _log_transition(self, source: State, target: State):
        msg = f"\n[{datetime.today()}] {self._testAnalyzer.sessionId} from: {source.name} to: {target.name}"
        f = open(f"state_machine_log_{self._testAnalyzer.get_fixture_ip()}.txt", "w")
        f.write(msg)
        f.close()
        if os.environ.get("ENV") == "testing":
            print(msg)

    def on_enter_Idle(self):
        self.update.emit(TestAnalysis(TestStatus.Idle))

    def on_enter_Recovered(self):
        self._refresh_testAnalyzer()
        self.update.emit(
            TestAnalysis(
                TestStatus.Recovered, startDateTime=self._testAnalyzer.get_start_time()
            )
        )

    def on_enter_Initialized(self):
        self._refresh_testAnalyzer()
        self._testAnalyzer.initialize_files()

    def on_enter_PreTested(self):
        self._emit_testAnalysis(
            "Pre-Test", TestStatus.PreTested, self._testAnalyzer.get_bmc_ip()
        )

    def _refresh_testAnalyzer(self):
        self._testAnalyzer.refresh_serial_number()
        self._testAnalyzer.refresh_mac()
        self._testAnalyzer.refresh_test_paths()
        self._testAnalyzer.call_get_bmc_ip()

    def on_enter_PreTestFailed(self):
        self._emit_testAnalysis("Pre-Test Failed")

    def on_enter_Tested(self):
        self._emit_testAnalysis(
            self._testAnalyzer.get_test_item(), bmcIp=self._testAnalyzer.get_bmc_ip()
        )

    def on_enter_Finished(self):
        self._emit_testAnalysis("Finished")

    def on_enter_Pass(self):
        self.update.emit(self._testAnalyzer.get_pass_test_analysis())

    def on_enter_Failed(self):
        self.update.emit(self._testAnalyzer.get_failed_test_analysis())

    def on_exit_Released(self):
        self.update.emit(TestAnalysis(TestStatus.Released))

    def _emit_testAnalysis(
        self, stepLabel: str, status: TestStatus = TestStatus.Tested, bmcIp: str = ""
    ):
        self.update.emit(
            TestAnalysis(
                status,
                stepLabel=stepLabel,
                bmcIp=bmcIp,
                serialNumber=self._testAnalyzer.get_serial_number(),
                mac=self._testAnalyzer.get_mac(),
            )
        )
