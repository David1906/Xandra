from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QComboBox,
    QTextEdit,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QCompleter,
    QShortcut,
    QFrame,
)
from PyQt5 import QtCore
from PyQt5.QtGui import QKeySequence, QRegExpValidator
from Models.Fixture import Fixture
from Models.Maintenance import Maintenance
from Utils.Translator import Translator
from Controllers.MaintenanceController import MaintenanceController

_ = Translator().gettext


class MaintenanceView(QFrame):
    MIN_EMP_LEN = 6
    MAX_DESCRIPTION_LEN = 255
    selected = QtCore.pyqtSignal(Maintenance)

    def __init__(
        self,
        parent: QWidget,
        fixtureId: str,
        fixtureIp: str,
        items: "list[str]",
        actions: "list[str]",
    ):
        super().__init__(parent)

        self.fixtureId = fixtureId
        self.fixtureIp = fixtureIp
        self._actions = actions
        self._items = items
        self._maintenanceController = MaintenanceController()

        self._init_ui()
        self._update_texts()

        self.msgSc = QShortcut(QKeySequence("Alt+Enter"), self.txtDescription)
        self.msgSc.activated.connect(self._save)

        self.items = items

    def _init_ui(self):
        layout = QGridLayout()

        self.setLayout(layout)

        self.lblInstruction = QLabel()
        # layout.addWidget(self.lblInstruction, 0, 0, 1, 3, QtCore.Qt.AlignCenter)

        self.lblPart = QLabel()
        layout.addWidget(self.lblPart, 1, 0)
        self.cboxPart = QComboBox()
        self.cboxPart.addItems(self.items)
        self.cboxPart.setEditable(True)
        layout.addWidget(self.cboxPart, 2, 0, 1, 3)

        self.lblAction = QLabel()
        layout.addWidget(self.lblAction, 3, 0)
        self.cboxAction = QComboBox()
        self.cboxAction.addItems(self.actions)
        layout.addWidget(self.cboxAction, 4, 0)

        self.lblEmployeeNumber = QLabel()
        layout.addWidget(self.lblEmployeeNumber, 3, 1)
        self.txtEmployeeNumber = QLineEdit()
        validator = QRegExpValidator(
            QtCore.QRegExp(f"[0-9]{{{MaintenanceView.MIN_EMP_LEN},9}}")
        )
        self.txtEmployeeNumber.setValidator(validator)
        layout.addWidget(self.txtEmployeeNumber, 4, 1)

        self.lblEmployeePassword = QLabel()
        layout.addWidget(self.lblEmployeePassword, 3, 2)
        self.txtPassword = QLineEdit()
        self.txtPassword.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.txtPassword, 4, 2)

        self.lblDescription = QLabel()
        layout.addWidget(self.lblDescription, 5, 0)
        self.txtDescription = QTextEdit()
        self.txtDescription.setMaximumHeight(30)
        self.txtDescription.textChanged.connect(self.on_txt_description_changed)
        layout.addWidget(self.txtDescription, 6, 0, 1, 3)
        self.lblDescriptionLen = QLabel(f"0/{MaintenanceView.MAX_DESCRIPTION_LEN}")
        layout.addWidget(self.lblDescriptionLen, 7, 2, QtCore.Qt.AlignRight)

        self.btnOk = QPushButton()
        self.btnOk.clicked.connect(self._save)
        layout.addWidget(self.btnOk, 8, 0, 1, 3, QtCore.Qt.AlignCenter)

        self.setStyleSheet(
            """
            MaintenanceView{  
               border: 1px solid #c0c2ce;
               background-color: #f8f8fa;
               border-radius: 3px;
            }
            """
        )
        self.setContentsMargins(0, 0, 0, 0)

    def _update_texts(self):
        self.lblInstruction.setText(
            _("* Enter the replaced part to unlock the fixture *")
        )
        self.lblPart.setText(_("Part *:"))
        self.lblAction.setText(_("Action *:"))
        self.lblEmployeeNumber.setText(_("Employee Number *:"))
        self.lblEmployeePassword.setText(_("Password *:"))
        self.lblDescription.setText(_("Description:"))
        self.btnOk.setText(_("&Save"))

    def _save(self):
        validation = self._validate()
        if validation != "":
            QMessageBox.warning(self, _("Error"), validation)
            return
        self.selected.emit(
            Maintenance(
                fixtureId=self.fixtureId,
                fixtureIp=self.fixtureIp,
                part=self.cboxPart.currentText(),
                employee=self.txtEmployeeNumber.text().strip().upper(),
                description=self.txtDescription.toPlainText().capitalize(),
                action=self.cboxAction.currentText(),
            )
        )
        self.reset()

    def _validate(self) -> str:
        error = _("{0} is required")
        labelTxt = ""
        if (
            not self.cboxPart.currentText() in self.items
            or self.cboxPart.currentText().strip() == ""
        ):
            labelTxt = self.lblPart.text()
        elif (
            not self.cboxAction.currentText() in self.actions
            or self.cboxAction.currentText().strip() == ""
        ):
            labelTxt = self.lblAction.text()
        elif self.txtEmployeeNumber.text().strip() == "":
            labelTxt = self.lblEmployeeNumber.text()
        elif not self.txtEmployeeNumber.hasAcceptableInput():
            error = _("{0} is invalid it should be at least {1} digits long").replace(
                "{1}", str(MaintenanceView.MIN_EMP_LEN)
            )
            labelTxt = self.lblEmployeeNumber.text()
        elif not self._maintenanceController.exists_employee(
            self.txtEmployeeNumber.text().strip()
        ):
            error = _(
                "Invalid {0} {1}.\n\nIf your number is correct, please contact the engineer."
            ).replace("{1}", self.txtEmployeeNumber.text().strip())
            labelTxt = self.lblEmployeeNumber.text()
        elif not self._maintenanceController.equals_password(
            self.txtEmployeeNumber.text().strip(),
            self.txtPassword.text().strip(),
        ):
            error = _(
                "Invalid {0}.\n\nIf your password is correct, please contact the engineer."
            )
            labelTxt = self.lblEmployeePassword.text()
        else:
            error = ""
        return error.format(labelTxt.replace(":", "").replace("*", "").strip())

    def reset(self):
        self.cboxPart.clear()
        self.cboxPart.addItems(self.items)
        self.txtEmployeeNumber.clear()
        self.txtPassword.clear()
        self.txtDescription.clear()

    def on_txt_description_changed(self):
        descriptionLen = len(self.txtDescription.toPlainText())
        if descriptionLen > MaintenanceView.MAX_DESCRIPTION_LEN:
            self.txtDescription.textCursor().deletePreviousChar()
        self.lblDescriptionLen.setText(
            f"{len(self.txtDescription.toPlainText())}/{MaintenanceView.MAX_DESCRIPTION_LEN}"
        )

    @property
    def items(self) -> "list[str]":
        return self._items

    @items.setter
    def items(self, value: "list[items]"):
        self._items = value
        self.cboxPart.clear()
        self.cboxPart.addItems(value)
        completer = QCompleter(self.items, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.cboxPart.setCompleter(completer)

    @property
    def actions(self) -> "list[str]":
        return self._actions

    @actions.setter
    def actions(self, value: "list[actions]"):
        self._actions = value
        self.cboxAction.clear()
        self.cboxAction.addItems(value)
