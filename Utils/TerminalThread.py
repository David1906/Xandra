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

    def __init__(self, fixtureId: str, sessionId: str):
        super().__init__()
        self._fixtureId = fixtureId
        self._analysisInterval = randint(700, 900) / 1000
        self._abort = False
        self._sessionId = sessionId
        self._sm = None
        self._terminalObserver = None

        self._testAnalyzer = TestAnalyzerBuilder().build_based_on_main_config(
            self._fixtureId, self._sessionId
        )
        self._terminalObserver = TestStateMachineObserver(None, self._testAnalyzer)
        self._terminalObserver.update.connect(self._terminal_updated)

    def run(self):
        while True:
            time.sleep(self._analysisInterval)
            try:
                if self._sm != None:
                    self._sm.cycle()
            except Exception as e:
                print("TerminalThread error: ", str(e))
                logging.error(str(e))
                self.reset()

    def pause(self):
        self._sm = None

    def reset(self):
        self._sm = TestStateMachine(testAnalyzer=self._testAnalyzer)
        self._sm.add_observer(self._terminalObserver)

    def _terminal_updated(self, testAnalysis: TestAnalysis):
        self.updated.emit(testAnalysis)
