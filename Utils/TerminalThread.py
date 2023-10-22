import debugpy
from Core.StateMachines.TeminalObserver import TemrinalObserver
from Core.StateMachines.TerminalStateMachine import TerminalStateMachine
from Models.TestAnalysis import TestAnalysis
from Products.TestAnalyzerBuilder import TestAnalyzerBuilder
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from random import randint
import time


class TerminalThread(QtCore.QThread):
    updated = pyqtSignal(TestAnalysis)

    def __init__(self, sessionId: str):
        super().__init__()
        self._analysisInterval = randint(700, 1000) / 1000
        self._abort = False
        self._sessionId = sessionId
        self._sm = None
        self._terminalObserver = None

    def run(self):
        debugpy.debug_this_thread()
        try:
            testAnalyzer = TestAnalyzerBuilder().build_based_on_main_config(
                self._sessionId
            )
            self._terminalObserver = TemrinalObserver(None, testAnalyzer)
            self._terminalObserver.update.connect(self._terminal_updated)
            self._sm = TerminalStateMachine(testAnalyzer=testAnalyzer)
            self._sm.add_observer(self._terminalObserver)
            while True:
                time.sleep(self._analysisInterval)
                self._sm.cycle()
        except Exception as e:
            print(str(e))

    def abort(self):
        # self._sm.stop()
        self.quit()

    def _terminal_updated(self, testAnalysis: TestAnalysis):
        self.updated.emit(testAnalysis)
