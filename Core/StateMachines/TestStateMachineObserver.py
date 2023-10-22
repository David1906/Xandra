from Core.Enums.TestStatus import TestStatus
from DataAccess.TestAnalyzer import TestAnalyzer
from Models.TestAnalysis import TestAnalysis
from Products.TestAnalyzerBuilder import TestAnalyzerBuilder
from PyQt5 import QtCore
from PyQt5.QtCore import QObject


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

    def on_enter_Idle(self):
        self.update.emit(TestAnalysis(TestStatus.Idle))

    def on_enter_Initialized(self):
        self._testAnalyzer.initialize_files()

    def on_enter_PreTested(self):
        self._testAnalyzer.refresh_serial_number()
        self._emit_testAnalysis("Pre-Test")

    def on_enter_PreTestFailed(self):
        self._emit_testAnalysis("Pre-Test Failed")

    def on_enter_Tested(self):
        self._emit_testAnalysis(self._testAnalyzer.get_test_item())

    def on_enter_Finished(self):
        self.update.emit(self._testAnalyzer.get_released_test_analysis())

    def _emit_testAnalysis(self, stepLabel: str):
        self.update.emit(TestAnalysis(TestStatus.Tested, stepLabel=stepLabel))
