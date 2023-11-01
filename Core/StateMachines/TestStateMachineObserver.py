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
        testAnalyzer: TestAnalyzer = None,
    ) -> None:
        super().__init__(parent)
        self._testAnalyzer = (
            testAnalyzer
            if testAnalyzer != None
            else TestAnalyzerBuilder().build_based_on_main_config()
        )
        self._isTransition = False

    def before_cycle(self, event: str, source: State, target: State, message: str = ""):
        self._isTransition = source.id != target.id
        if os.environ.get("ENV") == "testing" and self._isTransition:
            print(
                "\n",
                self._testAnalyzer.sessionId,
                "from: ",
                source.name,
                "to:",
                target.name,
            )

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
        self._emit_testAnalysis("Pre-Test")

    def _refresh_testAnalyzer(self):
        self._testAnalyzer.refresh_serial_number()
        self._testAnalyzer.refresh_test_paths()

    def on_enter_PreTestFailed(self):
        self._emit_testAnalysis("Pre-Test Failed")

    def on_enter_Tested(self):
        self._emit_testAnalysis(
            self._testAnalyzer.get_test_item(), self._testAnalyzer.get_bmc_ip()
        )

    def on_enter_Finished(self):
        self._emit_testAnalysis("Waiting for release")

    def on_enter_Pass(self):
        if self._isTransition:
            self.update.emit(self._testAnalyzer.get_pass_test_analysis())

    def on_enter_Failed(self):
        if self._isTransition:
            self.update.emit(self._testAnalyzer.get_failed_test_analysis())

    def _emit_testAnalysis(self, stepLabel: str, bmcIp: str = ""):
        self.update.emit(
            TestAnalysis(TestStatus.Tested, stepLabel=stepLabel, bmcIp=bmcIp)
        )
