from Controllers.FixtureController import FixtureController
from Models.Fixture import Fixture
from Models.Test import Test
from PyQt5 import QtCore
from PyQt5.QtWidgets import QGroupBox, QLabel, QPushButton, QGridLayout, QMessageBox
from Views.EmbeddedTerminal import EmbeddedTerminal
from Views.LastFailuresWindow import LastFailuresWindow
from Views.LastTestsWindow import LastTestsWindow
from Views.LedIndicator import LedIndicator
from Views.Switch import Switch


class FixtureView(QGroupBox):
    def __init__(self, fixture: Fixture):
        super().__init__()

        self.fixture = fixture
        self.w = None
        self._fixtureController = FixtureController()

        self.setObjectName("fixture")
        gridLayout = QGridLayout()
        self.setLayout(gridLayout)

        self.lblIp = QLabel("IP:")
        gridLayout.addWidget(self.lblIp, 0, 0, 1, 2, QtCore.Qt.AlignLeft)

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(self.on_btnStart_clicked)
        gridLayout.addWidget(self.btnStart, 0, 3, 1, 2, QtCore.Qt.AlignLeft)

        self.lblTraceability = QLabel("Traceability")
        gridLayout.addWidget(self.lblTraceability, 0, 5)
        self.swTraceability = Switch()
        self.swTraceability.setChecked(not fixture.isSkipped)
        self.swTraceability.toggled.connect(self.on_swTraceability_change)
        gridLayout.addWidget(self.swTraceability, 0, 6)

        self.lblYield = QLabel("Yield:")
        gridLayout.addWidget(self.lblYield, 2, 0, 1, 2)

        self.lblPassed = QLabel("Passed Last 3 Tests :")
        gridLayout.addWidget(self.lblPassed, 2, 5, 1, 1)
        self.led = LedIndicator()
        self.led.setEnabled(False)
        gridLayout.addWidget(self.led, 2, 6, 1, 1, QtCore.Qt.AlignRight)

        self.terminal = EmbeddedTerminal()
        self.terminal.finished.connect(self.on_terminal_finished)
        gridLayout.addWidget(self.terminal, 3, 0, 8, 7)

        self.btnLastTests = QPushButton("Last Tests")
        self.btnLastTests.clicked.connect(self.on_btnLastTests_clicked)
        gridLayout.addWidget(self.btnLastTests, 11, 0)

        self.btnLastFailures = QPushButton("Last Failures")
        self.btnLastFailures.clicked.connect(self.on_btnLastFailures_clicked)
        gridLayout.addWidget(self.btnLastFailures, 11, 1)

        self.lblResult = QLabel("Status: IDLE")
        gridLayout.addWidget(self.lblResult, 11, 2, 1, 5, QtCore.Qt.AlignRight)

        self.set_fixture(fixture)

    def on_btnLastTests_clicked(self):
        self.w = LastTestsWindow(self.fixture.ip)
        self.w.showMaximized()

    def on_btnLastFailures_clicked(self):
        self.w = LastFailuresWindow(self.fixture.ip)
        self.w.showMaximized()

    def on_swTraceability_change(self, checked: bool):
        self.fixture.isSkipped = not checked
        self._fixtureController.update(self.fixture)
        self._update()

    def set_fixture(self, fixture: Fixture):
        self.fixture = fixture
        self._update()

    def _update(self):
        self.lblResult.setText(self.fixture.get_status_string())
        self.lblYield.setText(f"Yield: {self.fixture.yieldRate}%")
        self.lblIp.setText(f"Ip: {self.fixture.ip}")
        self.lblPassed.setText(
            f"Passed Last {self._fixtureController.get_last_test_pass_qty()} Tests:"
        )
        self.led.setChecked(self.fixture.areLastTestPass)
        self.btnStart.setEnabled(
            not self.fixture.is_disabled() or self.btnStart.text() == "Stop"
        )

        self.setStyleSheet(
            f"""
            QGroupBox#fixture{{
                border-radius: 5px;
                border: 1px solid gray;
                background-color: {self.fixture.get_status_color()};
            }}
            """
        )

    def on_btnStart_clicked(self):
        isStart = self.btnStart.text() == "Start"
        self.swTraceability.setEnabled(not isStart)
        if isStart:
            cmd = self._fixtureController.get_fct_host_cmd(
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

    def on_terminal_finished(self, exitStatus):
        self.btnStart.setText("Start")
        self.swTraceability.setEnabled(True)

    def equals(self, fixture: Fixture) -> bool:
        return fixture.id == self.fixture.id

    def equalsIp(self, fixtureIp: str) -> bool:
        return self.fixture.ip == fixtureIp

    def set_fixture_isTesting (self, value: bool):
        self.fixture.set_isTesting(value)
        self._update()
 