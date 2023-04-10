from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal


class EmbeddedTerminal(QtWidgets.QFrame):
    finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.on_finished)

        self.terminal = QtWidgets.QFrame()
        self.setStyleSheet(
            """
            border-radius: 5px;
            border: 1px solid #cccccc; 
            background-color: #e6ebe7;
            """
        )

    def start(self, args: "list[str]" = []):
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
        ]
        fullArgs = fullArgs + args
        self.process.start("xterm", fullArgs)

    def on_finished(self, exitCode, exitStatus):
        self.finished.emit(exitCode)

    def Stop(self):
        self.process.kill()

    def get_terminal_winId(self) -> str:
        return str(int(self.winId()))
