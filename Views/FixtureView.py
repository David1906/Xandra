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
        self.forceTraceabilityEnabled = False
        self.w = None
        self._fixtureController = FixtureController()

        self.setObjectName("fixture")
        gridLayout = QGridLayout()
        self.setLayout(gridLayout)

        self.lblRetestMode = QLabel("Retest Mode")
        gridLayout.addWidget(self.lblRetestMode, 0, 5)
        self.swRetestMode = Switch()
        self.swRetestMode.setChecked(fixture.is_retest_mode())
        self.swRetestMode.toggled.connect(self.on_swRetestMode_change)
        gridLayout.addWidget(self.swRetestMode, 0, 6)
        self.set_retest_mode_visibility(False)

        self.lblIp = QLabel("IP:")
        gridLayout.addWidget(self.lblIp, 1, 0, 1, 2, QtCore.Qt.AlignLeft)

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(self.on_btnStart_clicked)
        gridLayout.addWidget(self.btnStart, 1, 3, 1, 2, QtCore.Qt.AlignLeft)

        self.lblTraceability = QLabel("Traceability")
        gridLayout.addWidget(self.lblTraceability, 1, 5)
        self.swTraceability = Switch()
        self.swTraceability.setChecked(not fixture.is_skipped())
        self.swTraceability.toggled.connect(self.on_swTraceability_change)
        gridLayout.addWidget(self.swTraceability, 1, 6)

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
        self.lblResult.setStyleSheet("font-size: 12px;")
        gridLayout.addWidget(self.lblResult, 11, 2, 1, 5, QtCore.Qt.AlignRight)

        self.set_fixture(fixture)

        self._updateTimer = QtCore.QTimer()
        self._updateTimer.timeout.connect(self._update_status)

    def on_btnLastTests_clicked(self):
        self.w = LastTestsWindow(self.fixture.get_ip())
        self.w.showMaximized()

    def on_btnLastFailures_clicked(self):
        self.w = LastFailuresWindow(self.fixture.get_ip())
        self.w.showMaximized()

    def on_swRetestMode_change(self, checked: bool):
        self.fixture.set_reset_mode(checked)
        self._update_sw_traceability_enabled()
        if not self.swTraceability.getChecked():
            self.swTraceability.setChecked(True)
        else:
            self._fixtureController.update(self.fixture)
            self._update()

    def on_swTraceability_change(self, checked: bool):
        self.fixture.set_skipped(not checked)
        self._fixtureController.update(self.fixture)
        self._update()

    def set_test(self, test: Test):
        self.fixture.set_test(test)
        self._fixtureController.add_test(self.fixture)
        self._fixtureController.refresh(self.fixture)
        self._update()

    def set_fixture(self, fixture: Fixture):
        self.fixture = fixture
        self._update()

    def _update(self):
        self._update_status()
        self.lblYield.setText(f"Yield: {self.fixture.get_yield()}%")
        self.lblIp.setText(f"Ip: {self.fixture.get_ip()}")
        self.lblPassed.setText(
            f"Passed Last {self._fixtureController.get_last_test_pass_qty()} Tests:"
        )
        self.led.setChecked(self.fixture.get_are_last_test_pass())
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

    def _update_status(self):
        if self.fixture != None:
            self.lblResult.setText(self.fixture.get_status_string())
            self.lblResult.setToolTip(self.fixture.errorMsg)

    def on_btnStart_clicked(self):
        isStart = self.btnStart.text() == "Start"
        self.swRetestMode.setEnabled(not isStart)
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
                f"Are you sure to stop fixture {self.fixture.get_id()}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.terminal.Stop()
                self.btnStart.setText("Start")
        self._update_sw_traceability_enabled()

    def _update_sw_traceability_enabled(self):
        isStart = self.btnStart.text() == "Start"
        if self.fixture.is_retest_mode() and not self.forceTraceabilityEnabled:
            self.swTraceability.setEnabled(False)
        else:
            self.swTraceability.setEnabled(isStart)

    def on_terminal_finished(self, exitStatus):
        self.btnStart.setText("Start")
        self.swRetestMode.setEnabled(True)
        self._update_sw_traceability_enabled()
        self.set_fixture_isTesting(False)

    def equals(self, fixture: Fixture) -> bool:
        return self.fixture.equals(fixture)

    def equalsIp(self, fixtureIp: str) -> bool:
        return self.fixture.equalsIp(fixtureIp)

    def set_fixture_isTesting(self, value: bool):
        self.fixture.set_isTesting(value)
        self._update()
        if value:
            self._updateTimer.start(1000)
        else:
            self._updateTimer.stop()

    def start(self):
        if self.btnStart.text() == "Start":
            self.on_btnStart_clicked()

    def stop(self):
        if self.btnStart.text() == "Stop":
            self.on_btnStart_clicked()

    def set_retest_mode_visibility(self, value):
        if value:
            self.lblRetestMode.show()
            self.swRetestMode.show()
        else:
            self.lblRetestMode.hide()
            self.swRetestMode.hide()

    def disableRetestMode(self):
        self.swRetestMode.setChecked(False)
        self._update()

    def toggle_force_traceability_enabled(self):
        self.forceTraceabilityEnabled = not self.forceTraceabilityEnabled
        self._update_sw_traceability_enabled()
