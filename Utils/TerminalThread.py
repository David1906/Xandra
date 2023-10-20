from Core.StateMachines.TeminalObserver import TemrinalObserver
from Core.StateMachines.TerminalStateMachine import TemrinalStatus, TerminalStateMachine
from Models.TerminalAnalysis import TerminalAnalysis
from Products.TerminalAnalyzerBuilder import TerminalAnalyzerBuilder
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from random import randint
import time
import logging


class TerminalThread(QtCore.QThread):
    updated = pyqtSignal(TerminalAnalysis)

    def __init__(self, sessionId: str):
        super().__init__()
        self._analysisInterval = randint(700, 1000) / 1000
        self._abort = False
        self._sessionId = sessionId
        self._sm = None
        self._terminalObserver = None

    def run(self):
        try:
            terminalAnalyzer = TerminalAnalyzerBuilder().build_based_on_main_config(
                self._sessionId
            )
            self._terminalObserver = TemrinalObserver(None, terminalAnalyzer)
            self._terminalObserver.update.connect(self._terminal_updated)
            self._sm = TerminalStateMachine(terminalAnalyzer=terminalAnalyzer)
            self._sm.add_observer(self._terminalObserver)

            while True:
                time.sleep(self._analysisInterval)
                self._sm.cycle()
        except Exception as e:
            msg = "Error in TerminalThread: " + str(e)
            logging.error(msg)
            print(msg)

    def stop(self):
        print("Terminal Thread Stop")
        self._sm.stop()

    def reset(self):
        print("Terminal Thread reset")
        self._sm.reset()

    def _terminal_updated(self, terminalAnalysis: TerminalAnalysis):
        self.updated.emit(terminalAnalysis)
