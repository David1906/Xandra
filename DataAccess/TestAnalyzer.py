from abc import abstractmethod
from Core.Enums.TestEvent import TestEvent
from Core.Enums.TestStatus import TestStatus
from Core.StateMachines.TestStateMachine import TestStateMachine
from datetime import datetime
from Core.StateMachines.TestStateMachineObserver import TestStateMachineObserver
from Models.Fixture import Fixture
from Models.NullTestAnalysis import NullTestAnalysis
from Models.TestAnalysis import TestAnalysis
from PyQt5 import QtCore
from random import randint
from statemachine import State
import logging
import os
import threading
import time


class TestAnalyzer(QtCore.QThread):
    initialized = QtCore.pyqtSignal()
    idle = QtCore.pyqtSignal()
    boardLoaded = QtCore.pyqtSignal(TestAnalysis)
    tested = QtCore.pyqtSignal(TestAnalysis)
    testFinished = QtCore.pyqtSignal(TestAnalysis)

    def __init__(self, fixture: Fixture, sessionId: str) -> None:
        super().__init__()
        self._serialNumber = ""
        self._mac = ""
        self._bmcIp = ""
        self._fixture = fixture
        self._sessionId = sessionId
        self._analysisInterval = randint(700, 900) / 1000
        self._lastAnalysis = NullTestAnalysis()
        self._threadEvent = threading.Event()
        self._stateMachine = TestStateMachine()
        self._stateMachine.add_observer(self)
        self._stateMachineObserver = TestStateMachineObserver(
            self._sessionId, self._fixture.ip
        )
        self._stateMachine.add_observer(self._stateMachineObserver)
        self._isStarted = False

    def run(self):
        self._debug_thread()
        if self.is_board_loaded():
            self.initialize_test()
        while True:
            try:
                if self.is_changed():
                    event = self.get_event()
                    if event != None:
                        eventName = event.name.lower()
                        self._stateMachine.send(eventName)
            except Exception as e:
                print("TestAnalyzer error: ", str(e))
                logging.error(str(e))
            finally:
                self._threadEvent.wait()
                time.sleep(self._analysisInterval)

    @abstractmethod
    def is_changed(self) -> bool:
        pass

    @abstractmethod
    def is_board_loaded(self) -> bool:
        pass

    @abstractmethod
    def get_event(self) -> TestEvent:
        pass

    @abstractmethod
    def initialize_test(self):
        pass

    @abstractmethod
    def get_test_analysis(
        self, testStatus: TestStatus, stepLabel: str = None
    ) -> TestAnalysis:
        pass

    def on_enter_Initialized(self):
        self.initialized.emit()

    def _debug_thread(self, sessionId: str = "console_1"):
        if os.environ.get("ENV") == "testing" and self._sessionId == sessionId:
            import debugpy

            debugpy.debug_this_thread()
            self._stateMachine._graph().write_png("./docs/assets/images/sm.png")

    def on_enter_Idle(self):
        self._serialNumber = ""
        self._mac = ""
        self._bmcIp = ""
        self.idle.emit()

    def on_enter_BoardLoaded(self):
        self.initialize_test()
        self.boardLoaded.emit(
            self.get_test_analysis(TestStatus.BoardLoaded, stepLabel="Board Lodaed")
        )

    def on_enter_Tested(self):
        self.tested.emit(self.get_test_analysis(TestStatus.Tested))

    def on_enter_Finished(self):
        self.testFinished.emit(self.get_test_analysis(TestStatus.Finished))

    def pause(self):
        self._threadEvent.clear()

    def reset(self):
        if not self._isStarted:
            self._isStarted = True
            self.start()
        if self._stateMachine.current_state_value != TestStatus.Initialized.value:
            self._stateMachine.release()
        self._threadEvent.set()
