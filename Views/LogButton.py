from PyQt5 import QtWidgets
import subprocess


class LogButton(QtWidgets.QPushButton):
    def __init__(self, fullPath: str, text: str = "Open") -> None:
        super().__init__(text)

        self._fullPath = (
            fullPath.replace(" ", "\ ").replace("(", "\(").replace(")", "\)")
        )
        self.clicked.connect(self.on_click)

    def on_click(self):
        subprocess.Popen(["gedit " + self._fullPath], shell=True)
