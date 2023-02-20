from PyQt5.QtWidgets import QFrame, QLabel, QPushButton, QGridLayout, QMessageBox
from PyQt5 import QtCore
from Controllers.FixtureController import FixtureController
from Models.Fixture import Fixture
from Views.EmbeddedTerminal import EmbeddedTerminal
from Views.LedIndicator import LedIndicator
from Views.Switch import Switch


class FixtureView(QFrame):
    def __init__(self, fixture: Fixture):
        super().__init__()

        self.fixture = fixture
        self._fixtureController = FixtureController()

        self.setProperty("cssClass", "large")
        gridLayout = QGridLayout()

        self.lblId = QLabel("Id:")
        self.lblId.setObjectName("h1")
        gridLayout.addWidget(self.lblId, 0, 0, 1, 5, QtCore.Qt.AlignCenter)

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(self.on_btnStart_clicked)
        gridLayout.addWidget(self.btnStart, 1, 0, 1, 5, QtCore.Qt.AlignCenter)

        self.lblIp = QLabel("IP:")
        gridLayout.addWidget(self.lblIp, 2, 0, 1, 2)

        self.lblYield = QLabel("Yield:")
        gridLayout.addWidget(self.lblYield, 3, 0, 1, 2)

        self.lblPassed = QLabel("Passed Last 3 Tests :")
        gridLayout.addWidget(self.lblPassed, 3, 3, 1, 1)
        self.led = LedIndicator()
        self.led.setEnabled(False)
        gridLayout.addWidget(self.led, 3, 4, 1, 1)

        self.lblTraceability = QLabel("Traceability")
        gridLayout.addWidget(self.lblTraceability, 2, 3)
        self.swTraceability = Switch()
        self.swTraceability.setChecked(True)
        self.swTraceability.toggled.connect(self.onSwTraceabilityChange)
        gridLayout.addWidget(self.swTraceability, 2, 4)

        self.lblSkip = QLabel("Skip Low Yield Lock")
        # gridLayout.addWidget(self.lblSkip, 3, 3)
        self.swSkip = Switch()
        self.swSkip.setEnabled(False)
        self.swSkip.toggled.connect(self.onswSkipChange)
        # gridLayout.addWidget(self.swSkip, 3, 4)

        self.terminal = EmbeddedTerminal()
        self.terminal.finished.connect(self.onTerminalFinished)
        gridLayout.addWidget(self.terminal, 5, 0, 8, 5)

        self.setLayout(gridLayout)
        self.__update()

    def onSwTraceabilityChange(self, checked: bool):
        self.swSkip.setChecked(not checked)

    def onswSkipChange(self, checked: bool):
        self.fixture.isSkipped = checked
        self._fixtureController.update_yield_lock_skipped(self.fixture)
        self.__update()

    def set_fixture(self, fixture: Fixture):
        self.fixture = fixture
        self.__update()

    def __update(self):
        self.lblId.setText(f"Fixture {self.fixture.id}")
        self.lblYield.setText(f"Yield: {self.fixture.yieldRate}%")
        self.lblIp.setText(f"Ip: {self.fixture.ip}")
        self.lblPassed.setText(
            f"Passed Last {self._fixtureController.get_last_test_pass_qty()} Tests:"
        )
        self.led.setChecked(self.fixture.areLastTestPass)

        objectName = ""
        if self.fixture.isDisabled():
            objectName = "error"
        elif self.fixture.isWarning():
            objectName = "warning"
        self.setObjectName(objectName)
        self.__setStyle()

    def __setStyle(self):
        self.setStyleSheet(
            """
            QWidget:disabled{
                opacity: 0.5;
            }
            QFrame[cssClass="large"] {
                margin: 2px;
                color: black;
                border-radius: 5px;
                border: 1px solid gray;
            }
            QFrame#error {
                background-color: lightcoral;
            }
            QFrame#warning {
                background-color: yellow;
            }
            QLabel#h1{
                margin: 5px 0x;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#h2{
                margin: 2px 0px;
                font-size: 16px;
            }
         """
        )

    def on_btnStart_clicked(self):
        if self.btnStart.text() == "Start":
            self.swTraceability.setChecked(True)
            cmd = self._fixtureController.get_launch_fct_host_cmd(
                self.fixture, self.swTraceability.getChecked()
            )
            print(cmd)
            self.terminal.start([cmd])
            self.btnStart.setText("Stop")
        else:
            reply = QMessageBox.question(
                self,
                "Stop Fixture",
                f"Are you sure to stop fixture {self.fixture.id}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.terminal.Stop()
                self.btnStart.setText("Start")

    def onTerminalFinished(self, exitStatus):
        self.btnStart.setText("Start")

    def equals(self, fixture) -> bool:
        return fixture.id == self.fixture.id
