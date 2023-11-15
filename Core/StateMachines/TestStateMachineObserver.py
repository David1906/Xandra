from Core.Enums.TestStatus import TestStatus
from DataAccess.TestAnalyzer import TestAnalyzer
from datetime import datetime
from Models.TestAnalysis import TestAnalysis
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
        if source.id != target.id:
            self._log_transition(source, target)

    def _log_transition(self, source: State, target: State):
        msg = f"\n[{datetime.today()}] {self._testAnalyzer.sessionId} from: {source.name} to: {target.name}"
        f = open(f"state_machine_log_{self._testAnalyzer.get_fixture_ip()}.txt", "a")
        f.write(msg)
        f.close()
        if os.environ.get("ENV") == "testing":
            print(msg)

    def on_enter_Idle(self):
        self.update.emit(TestAnalysis(TestStatus.Idle))

    def on_enter_Recovered(self):
        self._testAnalyzer.refresh_board_data()
        self.update.emit(self._testAnalyzer.get_test_analysis(TestStatus.Recovered))

    def on_enter_Initialized(self):
        self._testAnalyzer.refresh_board_data()
        self._testAnalyzer.initialize_files()

    def on_enter_PreTested(self):
        self.update.emit(
            self._testAnalyzer.get_test_analysis(TestStatus.PreTested, "Pre-Test")
        )

    def on_enter_PreTestFailed(self):
        self.update.emit(
            self._testAnalyzer.get_test_analysis(
                TestStatus.PreTested, "Pre-Test Failed"
            )
        )

    def on_enter_Tested(self):
        self.update.emit(self._testAnalyzer.get_test_analysis(TestStatus.Tested))

    def on_enter_Finished(self):
        self.update.emit(
            self._testAnalyzer.get_test_analysis(TestStatus.Tested, "Finished")
        )

    def on_enter_Pass(self):
        self.update.emit(self._testAnalyzer.get_test_analysis(TestStatus.Pass))

    def on_enter_Failed(self):
        self.update.emit(self._testAnalyzer.get_test_analysis(TestStatus.Failed))

    def on_exit_Released(self):
        self.update.emit(TestAnalysis(TestStatus.Released))
