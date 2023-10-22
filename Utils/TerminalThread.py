import debugpy
from Core.StateMachines.TestStateMachineObserver import TestStateMachineObserver
from Core.StateMachines.TestStateMachine import TestStateMachine
from Models.TestAnalysis import TestAnalysis
from Products.TestAnalyzerBuilder import TestAnalyzerBuilder
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from random import randint
import time
import logging


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
            self._terminalObserver = TestStateMachineObserver(None, testAnalyzer)
            self._terminalObserver.update.connect(self._terminal_updated)
            self._sm = TestStateMachine(testAnalyzer=testAnalyzer)
            self._sm.add_observer(self._terminalObserver)
            while True:
                time.sleep(self._analysisInterval)
                self._sm.cycle()
        except Exception as e:
            print(str(e))

    def abort(self):
        # self._sm.stop()
        self.quit()

    def reset(self):
        # TODO
        pass

    def _terminal_updated(self, testAnalysis: TestAnalysis):
        self.updated.emit(testAnalysis)
