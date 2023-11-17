from Models.Fixture import Fixture
from Models.NullTestAnalysis import NullTestAnalysis
from Models.TestAnalysis import TestAnalysis
from Products.TestAnalyzerBuilder import TestAnalyzerBuilder
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from subprocess import call
from threading import Thread
from time import sleep
import subprocess


class Terminal(QtWidgets.QFrame):
    AUTOMATIC_SELECTION_DELAY = 5
    finished = pyqtSignal(int)
    initialized = QtCore.pyqtSignal()
    idle = QtCore.pyqtSignal()
    boardLoaded = QtCore.pyqtSignal(TestAnalysis)
    tested = QtCore.pyqtSignal(TestAnalysis)
    testFinished = QtCore.pyqtSignal(TestAnalysis)

    def __init__(self, fixture: Fixture, automaticProductSelection: int = -1):
        super().__init__()
        self.isAnalazyng = False
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.on_finished)

        self.automaticProductSelection = automaticProductSelection
        self._fixture = fixture
        self.sessionId = f"console_{fixture.id}"
        self.terminal = QtWidgets.QFrame()
        self.lastAnalysis = NullTestAnalysis()
        self.setStyleSheet(
            """
            border-radius: 3px;
            border: 1px solid #c0c2ce; 
            background-color: #e5e6eb;
            """
        )

        self._testAnalyzer = TestAnalyzerBuilder().build_based_on_main_config(
            self._fixture, self.sessionId
        )
        self._testAnalyzer.initialized.connect(self.initialized.emit)
        self._testAnalyzer.idle.connect(self.idle.emit)
        self._testAnalyzer.boardLoaded.connect(self.boardLoaded.emit)
        self._testAnalyzer.tested.connect(self.tested.emit)
        self._testAnalyzer.testFinished.connect(self.testFinished.emit)

    def start(self, args: "list[str]" = []):
        self.create_tmux_session(";".join(args))
        fullArgs = [
            "-into",
            self.get_terminal_winId(),
            "-si",
            "-geometry",
            "120x30",
            "-sl",
            "2000",
            "-bg",
            "black",
            "-fg",
            "white",
            "-e",
            f"TMUX='' tmux attach-session -t {self.sessionId};",
        ]
        self.process.start("xterm", fullArgs)
        self._testAnalyzer.reset()

    def create_tmux_session(self, command: str):
        if not self.has_tmux_session():
            call(
                f"TMUX='' tmux new-session -A -s {self.sessionId} \; detach", shell=True
            )
            call(
                self._get_tmux_send_keys(f'"{command} ; exit"') + " Enter",
                shell=True,
            )
            self.set_tmux_option("status", "off")
            self.set_tmux_option("history-limit", "3000")
            self.set_tmux_option("mouse", "on")
            self.set_tmux_option("mode-keys", "vi")
            Thread(target=self.automatic_product_selection).start()

    def has_tmux_session(self) -> bool:
        returnCode = subprocess.call(
            f"tmux has-session -t {self.sessionId}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        return returnCode == 0

    def set_tmux_option(self, option: str, value: str):
        call(f"tmux set-option -t {self.sessionId} {option} {value}", shell=True)

    def automatic_product_selection(self):
        if self.automaticProductSelection == -1:
            return
        while not self._is_ready_to_select_product():
            sleep(0.5)
        subprocess.Popen(
            f"""{self._get_tmux_send_keys(f"Down " * self.automaticProductSelection)}; 
            sleep .5; 
            {self._get_tmux_send_keys("Enter")};""".strip(),
            shell=True,
        )

    def _is_ready_to_select_product(self) -> bool:
        return self._buffer_contains("What's your product model?")

    def _buffer_contains(self, regex: str) -> bool:
        p1 = subprocess.Popen(
            ["tmux", "capture-pane", "-t", self.sessionId, "-pS", "-"],
            stdout=subprocess.PIPE,
        )
        p2 = subprocess.Popen(
            ["grep", "-Poi", regex], stdin=p1.stdout, stdout=subprocess.PIPE
        )
        p1.stdout.close()
        p2.communicate()
        return p2.returncode == 0

    def _get_tmux_send_keys(self, keys: str) -> str:
        return f"tmux send-keys -t {self.sessionId} {keys}"

    def on_finished(self, exitCode, exitStatus):
        print("Finished ", self.sessionId, exitCode, exitStatus)
        self.lastAnalysis = NullTestAnalysis()
        self._testAnalyzer.pause()
        self.finished.emit(exitCode)

    def Stop(self):
        call(f"tmux kill-session -t {self.sessionId}", shell=True)
        self.process.kill()

    def get_terminal_winId(self) -> str:
        return str(int(self.winId()))

    def _terminal_updated(self, testAnalysis: TestAnalysis):
        self.change.emit(testAnalysis)
