import re
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox


class ExitSingleInstanceWindow(QMessageBox):
    def __init__(self):
        super().__init__(
            QMessageBox.Warning,
            "Xandra is already open",
            "Xandra is already open, please close the main window to allow a new start",
        )
        self.setStandardButtons(QMessageBox.Ok)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("..."), QtGui.QIcon.Normal)
        self.setWindowIcon(icon)

    def exec(self, error: str) -> int:
        if not re.match(".*resource temporarily unavailable.*", error, re.IGNORECASE):
            self.setWindowTitle(
                "Xandra Error",
            )
            self.setText(f"Please verify the config file\n\n{error}")
        return super().exec()
