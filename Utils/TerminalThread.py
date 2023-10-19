from Core.StateMachines.TeminalObserver import TemrinalObserver
from Core.StateMachines.TerminalStateMachine import TerminalStateMachine
from Models.TerminalAnalysis import TerminalAnalysis
from Products.TerminalAnalyzerBuilder import TerminalAnalyzerBuilder
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from random import randint
import time


class TerminalThread(QtCore.QThread):
    updated = pyqtSignal(TerminalAnalysis)
    analysisInterval = randint(700, 1100) / 1000

    def __init__(self, sessionId: str):
        super().__init__()
        self._abort = False
        self.sessionId = sessionId
        self.sm = None
        self.terminalObserver = None

    def run(self):
        self._abort = False
        terminalAnalyzer = TerminalAnalyzerBuilder().build_based_on_main_config(
            self.sessionId
        )
        self.terminalObserver = TemrinalObserver(None, terminalAnalyzer)
        self.terminalObserver.update.connect(self._terminal_updated)
        self.sm = TerminalStateMachine(terminalAnalyzer=terminalAnalyzer)
        self.sm.add_observer(self.terminalObserver)

        while not self._abort:
            time.sleep(self.analysisInterval)
            self.sm.cycle()

    def abort(self):
        self._abort = True
        self.quit()

    def _terminal_updated(self, terminalAnalysis: TerminalAnalysis):
        self.updated.emit(terminalAnalysis)
