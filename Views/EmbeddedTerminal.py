from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal


class EmbeddedTerminal(QtWidgets.QWidget):
    finished = pyqtSignal(int)

    def __init__(self):
        super(EmbeddedTerminal, self).__init__()
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.on_finished)

        gridLayout = QtWidgets.QGridLayout()
        self.terminal = QtWidgets.QFrame()
        gridLayout.addWidget(self.terminal, 0, 0)
        self.setLayout(gridLayout)
        self.terminal.setStyleSheet(
            "border: 1px solid gray; background-color: lightgray; margin: 0;"
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
        return str(int(self.terminal.winId()))
