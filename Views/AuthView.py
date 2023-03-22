from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QErrorMessage
import hashlib
import os


class AuthView(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.isAuthorized = False

    def interact(self):
        password, done1 = QInputDialog().getText(
            self, "Enable Retest Mode", "Enter password:", echo=QLineEdit.Password
        )
        password = os.environ.get("HALT") + password
        self.isAuthorized = hashlib.md5(password.encode()).hexdigest() in [
            "ee2a79379665ff21d390236e0c0a35be",
            "11af4a833d8ef86da1edff462e9e0c74",
            "8c18593c2bb8e7f4eb0642fb0d471eaa",
        ]
        if not self.isAuthorized:
            error_dialog = QErrorMessage(self)
            error_dialog.showMessage("Wrong password")
            error_dialog.exec_()
