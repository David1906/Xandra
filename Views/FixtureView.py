from Controllers.FixtureController import FixtureController
from Models.Fixture import Fixture
from PyQt5 import QtCore
from PyQt5.QtWidgets import QGroupBox, QLabel, QPushButton, QGridLayout, QMessageBox
from Models.Test import Test
from Views.EmbeddedTerminal import EmbeddedTerminal
from Views.LastFailuresWindow import LastFailuresWindow
from Views.LastTestsWindow import LastTestsWindow
from Views.LedIndicator import LedIndicator
from Views.Switch import Switch


class FixtureView(QGroupBox):
    def __init__(self, fixture: Fixture):
        super().__init__()

        self.fixture = fixture
        self.test = None
        self.w = None
        self._fixtureController = FixtureController()

        self.setObjectName("fixture")
        gridLayout = QGridLayout()
        self.setLayout(gridLayout)

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(self.onBtnStartClicked)
        gridLayout.addWidget(self.btnStart, 0, 0, 1, 5, QtCore.Qt.AlignCenter)

        self.lblIp = QLabel("IP:")
        gridLayout.addWidget(self.lblIp, 1, 0, 1, 2)

        self.lblTraceability = QLabel("Traceability")
        gridLayout.addWidget(self.lblTraceability, 1, 3)
        self.swTraceability = Switch()
        self.swTraceability.setChecked(True)
        self.swTraceability.toggled.connect(self.onSwTraceabilityChange)
        gridLayout.addWidget(self.swTraceability, 1, 4)

        self.lblYield = QLabel("Yield:")
        gridLayout.addWidget(self.lblYield, 2, 0, 1, 2)

        self.lblPassed = QLabel("Passed Last 3 Tests :")
        gridLayout.addWidget(self.lblPassed, 2, 3, 1, 1)
        self.led = LedIndicator()
        self.led.setEnabled(False)
        gridLayout.addWidget(self.led, 2, 4, 1, 1)

        self.terminal = EmbeddedTerminal()
        self.terminal.finished.connect(self.onTerminalFinished)
        gridLayout.addWidget(self.terminal, 3, 0, 8, 5)

        self.btnLastTests = QPushButton("Last Tests")
        self.btnLastTests.clicked.connect(self.onBtnLastTestsClicked)
        gridLayout.addWidget(self.btnLastTests, 11, 0)

        self.btnLastFailures = QPushButton("Last Failures")
        self.btnLastFailures.clicked.connect(self.onBtnLastFailuresClicked)
        gridLayout.addWidget(self.btnLastFailures, 11, 1)

        self.lblResult = QLabel("Status: IDLE")
        gridLayout.addWidget(self.lblResult, 11, 2, 1, 3, QtCore.Qt.AlignRight)

        self.setFixture(fixture)

    def onBtnLastTestsClicked(self):
        self.w = LastTestsWindow(self.fixture.ip)
        self.w.showMaximized()

    def onBtnLastFailuresClicked(self):
        self.w = LastFailuresWindow(self.fixture.ip)
        self.w.showMaximized()

    def onSwTraceabilityChange(self, checked: bool):
        self.fixture.isSkipped = not checked
        self._fixtureController.update(self.fixture)
        self.__updateFixture()

    def setFixture(self, fixture: Fixture):
        self.fixture = fixture
        self.__updateFixture()

    def setTest(self, test: Test):
        self.test = test
        self.__updateTest()

    def __updateTest(self):
        self.lblResult.setText(f"Result: {self.test.getResultString()}")

    def __updateFixture(self):
        self.lblYield.setText(f"Yield: {self.fixture.yieldRate}%")
        self.lblIp.setText(f"Ip: {self.fixture.ip}")
        self.lblPassed.setText(
            f"Passed Last {self._fixtureController.getLastTestPassQty()} Tests:"
        )
        self.led.setChecked(self.fixture.areLastTestPass)
        self.btnStart.setEnabled(
            not self.fixture.isDisabled() or self.btnStart.text() == "Stop"
        )

        background = ""
        if self.fixture.isDisabled():
            background = "background-color: lightcoral;"
        elif self.fixture.isWarning():
            background = "background-color: yellow;"

        self.setStyleSheet(
            f"""
            QGroupBox#fixture{{
                border-radius: 5px;
                border: 1px solid gray;
                {background}
            }}
            """
        )

    def onBtnStartClicked(self):
        isStart = self.btnStart.text() == "Start"
        self.swTraceability.setEnabled(not isStart)
        if isStart:
            cmd = self._fixtureController.getLaunchFctHostCmd(
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
        self.swTraceability.setEnabled(True)

    def equals(self, fixture) -> bool:
        return fixture.id == self.fixture.id
