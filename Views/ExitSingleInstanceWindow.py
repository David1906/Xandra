import re
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox
from Utils.Translator import Translator

_ = Translator().gettext


class ExitSingleInstanceWindow(QMessageBox):
    def __init__(self):
        super().__init__(
            QMessageBox.Warning,
            _("Xandra Error"),
            _(
                "Xandra is already open, please close the main window to allow a new start\n\nIf you need a force close, enter the command xandra-kill in a terminal."
            ),
        )
        self.setStandardButtons(QMessageBox.Ok)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("..."), QtGui.QIcon.Normal)
        self.setWindowIcon(icon)

    def exec(self, error: str) -> int:
        if not re.match(".*resource temporarily unavailable.*", error, re.IGNORECASE):
            self.setWindowTitle(
                _("Xandra Error"),
            )
            self.setText(_("Please verify the config file") + f"\n\n{error}")
        return super().exec()
