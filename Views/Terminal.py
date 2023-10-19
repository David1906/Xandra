from random import randint
from subprocess import call, run
from time import sleep
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from Core.StateMachines.TeminalObserver import TemrinalObserver
from Core.StateMachines.TerminalStateMachine import TerminalStateMachine
from Models.NullTerminalAnalysis import NullTerminalAnalysis
from Models.TerminalAnalysis import TerminalAnalysis
from Products.TerminalAnalyzerBuilder import TerminalAnalyzerBuilder


class Terminal(QtWidgets.QFrame):
    analysisInterval = 1000 + randint(0, 500)
    finished = pyqtSignal(int)
    change = pyqtSignal(TerminalAnalysis)

    def __init__(self, id: str):
        super().__init__()
        self.isAnalazyng = False
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.on_finished)

        self.sessionId = f"console_{id}"
        self.terminal = QtWidgets.QFrame()
        self._analyzer = TerminalAnalyzerBuilder().build_based_on_main_config(
            self.sessionId
        )
        self.lastAnalysis = NullTerminalAnalysis()
        self.setStyleSheet(
            """
            border-radius: 5px;
            border: 1px solid #cccccc; 
            background-color: #e6ebe7;
            """
        )

        terminalAnalyzer = TerminalAnalyzerBuilder().build_based_on_main_config(
            self.sessionId
        )
        self._sm = TerminalStateMachine(terminalAnalyzer=terminalAnalyzer)
        self._terminalObserver = TemrinalObserver(self, terminalAnalyzer)
        self._terminalObserver.update.connect(self._terminal_updated)
        self._sm.add_observer(self._terminalObserver)

        self._updateTimer = QtCore.QTimer()
        self._updateTimer.timeout.connect(self._sm.cycle)

    def keyPressEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.key() == QtCore.Qt.Key_R:
                print("Ctrl + R")

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
        self._updateTimer.start(self.analysisInterval)

    def create_tmux_session(self, command: str):
        tmuxSession = run(["tmux", "has-session", "-t", self.sessionId])
        if tmuxSession.returncode != 0:
            call(
                f"TMUX='' tmux new-session -A -s {self.sessionId} \; detach", shell=True
            )
            call(
                f'tmux send-keys -t {self.sessionId} "{command} || exit" Enter',
                shell=True,
            )
            self.set_tmux_option("status", "off")
            self.set_tmux_option("history-limit", "3000")
            self.set_tmux_option("mouse", "on")
            self.set_tmux_option("mode-keys", "vi")

    def set_tmux_option(self, option: str, value: str):
        call(f"tmux set-option -t {self.sessionId} {option} {value}", shell=True)

    def on_finished(self, exitCode, exitStatus):
        self.finished.emit(exitCode)
        self._updateTimer.stop()

    def Stop(self):
        call(f"tmux kill-session -t {self.sessionId}", shell=True)
        self.process.kill()

    def get_terminal_winId(self) -> str:
        return str(int(self.winId()))

    def _terminal_updated(self, terminalAnalysis: TerminalAnalysis):
        if terminalAnalysis.is_stopped():
            self.Stop()
            return
        if not self.lastAnalysis.equals(terminalAnalysis):
            self.change.emit(terminalAnalysis)
        self.lastAnalysis = terminalAnalysis
