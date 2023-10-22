from subprocess import call, run
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from Models.NullTestAnalysis import NullTestAnalysis
from Models.TestAnalysis import TestAnalysis
from Utils.TerminalThread import TerminalThread


class Terminal(QtWidgets.QFrame):
    finished = pyqtSignal(int)
    change = pyqtSignal(TestAnalysis)

    def __init__(self, id: str):
        super().__init__()
        self.isAnalazyng = False
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.on_finished)

        self.sessionId = f"console_{id}"
        self.terminal = QtWidgets.QFrame()
        self.lastAnalysis = NullTestAnalysis()
        self.setStyleSheet(
            """
            border-radius: 5px;
            border: 1px solid #cccccc; 
            background-color: #e6ebe7;
            """
        )

        self.terminalThread = TerminalThread(self.sessionId)
        self.terminalThread.updated.connect(self._terminal_updated)

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
        self.terminalThread.start(priority=QtCore.QThread.Priority.HighPriority)

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
        self.terminalThread.abort()
        self.finished.emit(exitCode)

    def Stop(self):
        call(f"tmux kill-session -t {self.sessionId}", shell=True)
        self.process.kill()

    def get_terminal_winId(self) -> str:
        return str(int(self.winId()))

    def _terminal_updated(self, testAnalysis: TestAnalysis):
        if not self.lastAnalysis.equals(testAnalysis):
            self.change.emit(testAnalysis)
        self.lastAnalysis = testAnalysis
