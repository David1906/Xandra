from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from Core.Enums.TerminalStatus import TerminalStatus
from DataAccess.TerminalAnalyzer import TerminalAnalyzer
from Models.TerminalAnalysis import TerminalAnalysis
from Products.TerminalAnalyzerBuilder import TerminalAnalyzerBuilder


class TemrinalObserver(QtCore.QObject):
    update = QtCore.pyqtSignal(TerminalAnalysis)

    def __init__(
        self,
        parent: QObject,
        terminalAnalyzer: TerminalAnalyzer = None,
    ) -> None:
        super().__init__(parent)
        self._terminalAnalyzer = (
            terminalAnalyzer
            if terminalAnalyzer != None
            else TerminalAnalyzerBuilder().build_based_on_main_config()
        )

    def on_enter_IDLE(self):
        self.update.emit(TerminalAnalysis(TerminalStatus.IDLE))

    def on_enter_Loaded(self):
        self._emit_terminalAnalysis("Board Loaded")

    def on_enter_PoweredOn(self):
        self._terminalAnalyzer.refresh_serial_number()
        self._terminalAnalyzer.initialize_files()
        self._emit_terminalAnalysis("Board Powered On")

    def on_enter_Tested(self):
        self._emit_terminalAnalysis(self._terminalAnalyzer.get_test_item())

    def on_enter_Finished(self):
        self.update.emit(self._terminalAnalyzer.get_finished_terminalAnalysis())

    def on_enter_Stopped(self):
        self.update.emit(TerminalAnalysis(TerminalStatus.IDLE))

    def _emit_terminalAnalysis(self, stepLabel: str):
        self.update.emit(TerminalAnalysis(TerminalStatus.TESTING, stepLabel=stepLabel))
