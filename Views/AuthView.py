from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QMessageBox
import hashlib
import os
from Utils.Translator import Translator

_ = Translator().gettext


class AuthView(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.isAuthorized = False

    def interact(self):
        done = True
        self.isAuthorized = False
        while done and not self.isAuthorized:
            password, done = QInputDialog().getText(
                self, _("Auth"), _("Enter password:"), echo=QLineEdit.Password
            )
            if done:
                password = os.environ.get("HALT") + password
                self.isAuthorized = hashlib.md5(password.encode()).hexdigest() in [
                    "ee2a79379665ff21d390236e0c0a35be",
                    "11af4a833d8ef86da1edff462e9e0c74",
                    "8c18593c2bb8e7f4eb0642fb0d471eaa",
                    'd92b490e0132a91b4035de263299f0e7',
                    '2edcd1ca50f6857fd9b96b5202a71e1a',
                    '0006e3c70bf2246301ebd1955688c717'
                ]
                if not self.isAuthorized:
                    QMessageBox.warning(self, _("Auth Error"), _("Wrong password"))
