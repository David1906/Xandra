from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal


class EmbededTerminal(QtWidgets.QWidget):
    finished = pyqtSignal(int)

    def __init__(self):
        super(EmbededTerminal, self).__init__()
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.onFinished)

        gridLayout = QtWidgets.QGridLayout()
        self.terminal = QtWidgets.QFrame()
        gridLayout.addWidget(self.terminal, 0, 0)
        self.setLayout(gridLayout)
        # self.terminal.setMinimumHeight(180)
        # self.terminal.setMinimumWidth(600)
        self.terminal.setStyleSheet(
            "border: 1px solid gray; background-color: lightgray;"
        )

    def start(self, args: "list[str]" = []):
        fullArgs = ["-embed", self.getTerminalWinId(), "-e", "sh", "-c"]
        fullArgs = fullArgs + args
        self.process.start("rxvt-unicode", fullArgs)

    def onFinished(self, exitCode, exitStatus):
        self.finished.emit(exitCode)

    def Stop(self):
        self.process.kill()

    def getTerminalWinId(self) -> str:
        return str(int(self.terminal.winId()))
