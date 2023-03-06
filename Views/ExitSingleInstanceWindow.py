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
