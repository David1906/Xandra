from subprocess import call
import subprocess
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from Models.NullTestAnalysis import NullTestAnalysis
from Models.TestAnalysis import TestAnalysis
from Utils.TerminalThread import TerminalThread


class Terminal(QtWidgets.QFrame):
    AUTOMATIC_SELECTION_DELAY = 5
    finished = pyqtSignal(int)
    change = pyqtSignal(TestAnalysis)

    def __init__(self, id: str, automaticProductSelection: int = -1):
        super().__init__()
        self.isAnalazyng = False
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.on_finished)

        self.automaticProductSelection = automaticProductSelection
        self.id = id
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

        self.terminalThread = TerminalThread(self.id, self.sessionId)
        self.terminalThread.updated.connect(self._terminal_updated)
        self.terminalThread.start(priority=QtCore.QThread.Priority.HighPriority)

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
        self.terminalThread.reset()

    def create_tmux_session(self, command: str):
        if not self.has_tmux_session():
            call(
                f"TMUX='' tmux new-session -A -s {self.sessionId} \; detach", shell=True
            )
            call(
                self._get_tmux_send_keys(f'"{command} || exit"') + " Enter",
                shell=True,
            )
            self.set_tmux_option("status", "off")
            self.set_tmux_option("history-limit", "3000")
            self.set_tmux_option("mouse", "on")
            self.set_tmux_option("mode-keys", "vi")
            self.automatic_product_selection()

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
        subprocess.Popen(
            f"""sleep {self.AUTOMATIC_SELECTION_DELAY}; 
            {self._get_tmux_send_keys(f"Down " * self.automaticProductSelection)}; 
            sleep .5; 
            {self._get_tmux_send_keys("Enter")};""".strip(),
            shell=True,
        )

    def _get_tmux_send_keys(self, keys: str) -> str:
        return f"tmux send-keys -t {self.sessionId} {keys}"

    def on_finished(self, exitCode, exitStatus):
        print("Finished ", self.sessionId, exitCode, exitStatus)
        self.lastAnalysis = NullTestAnalysis()
        self.terminalThread.pause()
        self.finished.emit(exitCode)

    def Stop(self):
        call(f"tmux kill-session -t {self.sessionId}", shell=True)
        self.process.kill()

    def get_terminal_winId(self) -> str:
        return str(int(self.winId()))

    def _terminal_updated(self, testAnalysis: TestAnalysis):
        self.change.emit(testAnalysis)
