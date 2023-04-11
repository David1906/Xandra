from Controllers.FixtureController import FixtureController
from Core.Enums.TestMode import TestMode
from Models.Fixture import Fixture
from Models.Test import Test
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QGroupBox,
    QLabel,
    QPushButton,
    QGridLayout,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
)
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
        self.lastOverElapsed = False
        self._fixtureController = FixtureController()

        self.setObjectName("fixture")
        gridLayout = QGridLayout()
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 0)
        gridLayout.setColumnMinimumWidth(1, 130)
        gridLayout.setRowStretch(0, 1)
        gridLayout.setRowStretch(1, 0)
        self.setLayout(gridLayout)

        sideGridLayout = QGridLayout()
        sideGridLayout.setRowStretch(0, 0)
        sideGridLayout.setRowStretch(1, 1)
        sideGridLayout.setRowStretch(2, 0)
        gridLayout.addLayout(sideGridLayout, 0, 1, 1, 1)

        infoLayout = QVBoxLayout()
        sideGridLayout.addLayout(infoLayout, 0, 0)

        self.lblYield = QLabel("Yield:")
        infoLayout.addWidget(self.lblYield, alignment=QtCore.Qt.AlignCenter)

        self.lblMode = QLabel("Mode:")
        infoLayout.addWidget(self.lblMode, alignment=QtCore.Qt.AlignCenter)

        self.lblIp = QLabel("IP:")
        infoLayout.addWidget(self.lblIp, alignment=QtCore.Qt.AlignCenter)

        selectorsLayout = QVBoxLayout()
        selectorsLayout.addStretch()
        sideGridLayout.addLayout(selectorsLayout, 1, 0)

        indicatorLayout = QHBoxLayout()
        self.lblLock = QLabel()
        indicatorLayout.addWidget(self.lblLock)
        self.led = LedIndicator()
        self.led.setEnabled(False)
        indicatorLayout.addWidget(self.led, alignment=QtCore.Qt.AlignRight)
        selectorsLayout.addLayout(indicatorLayout)

        traceabilityLayout = QHBoxLayout()
        self.lblTraceability = QLabel("Traceability")
        traceabilityLayout.addWidget(self.lblTraceability)
        self.swTraceability = Switch()
        self.swTraceability.setChecked(not fixture.is_skipped())
        self.swTraceability.toggled.connect(self.on_swTraceability_change)
        traceabilityLayout.addWidget(
            self.swTraceability, alignment=QtCore.Qt.AlignRight
        )
        selectorsLayout.addLayout(traceabilityLayout)

        retestLayout = QHBoxLayout()
        self.lblRetestMode = QLabel("Retest Mode")
        retestLayout.addWidget(self.lblRetestMode)
        self.swRetestMode = Switch()
        self.swRetestMode.setChecked(fixture.is_retest_mode())
        self.swRetestMode.toggled.connect(self.on_swRetestMode_change)
        self.set_retest_mode_visibility(False)
        retestLayout.addWidget(self.swRetestMode, alignment=QtCore.Qt.AlignRight)
        selectorsLayout.addLayout(retestLayout)

        selectorsLayout.addStretch()

        buttonsLayout = QVBoxLayout()
        self.btnStart = QPushButton("Start")
        self.btnStart.setStyleSheet("font-size: 12px; font-weight: 300;")
        self.btnStart.setFixedHeight(50)
        self.btnStart.clicked.connect(self.on_btnStart_clicked)
        buttonsLayout.addWidget(self.btnStart)

        sideGridLayout.addLayout(buttonsLayout, 2, 0)
        self.btnLastTests = QPushButton("Last Tests")
        self.btnLastTests.clicked.connect(self.on_btnLastTests_clicked)
        buttonsLayout.addWidget(self.btnLastTests)

        self.btnLastFailures = QPushButton("Last Failures")
        self.btnLastFailures.clicked.connect(self.on_btnLastFailures_clicked)
        buttonsLayout.addWidget(self.btnLastFailures)

        self.terminal = EmbeddedTerminal()
        self.terminal.finished.connect(self.on_terminal_finished)
        gridLayout.addWidget(self.terminal, 0, 0, 1, 1)

        self.lblResult = QLabel("Status: IDLE")
        self.lblResult.setStyleSheet("font-size: 12px; font-weight: bold; margin: 5px;")
        gridLayout.addWidget(
            self.lblResult, 2, 0, 1, 3, alignment=QtCore.Qt.AlignCenter
        )

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
            self.update()

    def on_swTraceability_change(self, checked: bool):
        self.fixture.set_skipped(not checked)
        self._fixtureController.update(self.fixture)
        self.update()

    def set_test(self, test: Test):
        self.fixture.set_test(test, self.swTraceability.getChecked())
        self._fixtureController.add_test(self.fixture)
        self._fixtureController.refresh(self.fixture)
        self.update()

    def set_fixture(self, fixture: Fixture):
        self.fixture = fixture
        self.update()

    def update(self):
        self._update_status()
        self.lblYield.setText(f"Yield: {self.fixture.get_yield()}%")
        self.lblIp.setText(f"Ip: {self.fixture.get_ip()}")
        self.lblLock.setText(
            f"Failed last {self._fixtureController.get_lock_fail_qty()} Tests:"
        )
        self.btnStart.setEnabled(
            not self.fixture.is_disabled() or self.btnStart.text() == "Stop"
        )
        self.lblMode.setText(f"Mode: {self.fixture.get_mode_description()}")
        self.update_lock_indicator()
        self._update_sw_retest_enabled()

        self.setStyleSheet(
            f"""
            QGroupBox#fixture{{
                border-radius: 5px;
                border: 1px solid #cccccc;
                background-color: {self.fixture.get_status_color()};
            }}
            """
        )

    def _update_status(self):
        if self.fixture != None:
            self.lblResult.setText(self.fixture.get_status_string())
            self.lblResult.setToolTip(self.fixture.get_status_description())
            if self.fixture.is_over_elapsed() != self.lastOverElapsed:
                self.lastOverElapsed = not self.lastOverElapsed
                self.lblResult.setStyleSheet(
                    f"color: {'red' if self.lastOverElapsed else 'black'};"
                )

    def update_lock_indicator(self):
        self.lblLock.setText(self.fixture.get_lock_description())
        isVisible = self.fixture.is_disabled()
        self.led.set_color_red()
        isLedOn = self.fixture.is_disabled()
        tooltipTxt = (
            f"Fixture locked due to {self.fixture.get_lock_description().lower()}"
        )

        if self.fixture.get_mode() == TestMode.OFFLINE:
            isVisible = True
            self.led.set_color_green()
            isLedOn = self.fixture.get_are_last_test_pass()
            tooltipTxt = f"Fixture unlocked"
            if not isLedOn:
                remainingToUnlock = self._fixtureController.get_remaining_to_unlock(
                    self.fixture
                )
                self.lblLock.setText(f"Test {remainingToUnlock} to unlock")
                tooltipTxt = f"Test another {remainingToUnlock} board{'s' if remainingToUnlock > 1 else ''} which result is pass to unlock the fixture"

        self.lblLock.setHidden(not isVisible)
        self.lblLock.setToolTip(tooltipTxt)
        self.led.setToolTip(tooltipTxt)
        self.led.setHidden(not isVisible)
        self.led.setChecked(isLedOn)

    def on_btnStart_clicked(self):
        isStart = self.btnStart.text() == "Start"
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
        self._update_sw_retest_enabled()
        self._update_sw_traceability_enabled()

    def on_terminal_finished(self, exitStatus):
        self.btnStart.setText("Start")
        self._update_sw_retest_enabled()
        self._update_sw_traceability_enabled()
        self.set_fixture_isTesting(False)

    def _update_sw_retest_enabled(self):
        isStart = self.btnStart.text() == "Start"
        isDisabled = self.fixture.is_disabled()
        if self.fixture.is_skipped():
            isDisabled = not self.fixture.get_are_last_test_pass()
        self.swRetestMode.setEnabled(isStart and not isDisabled)

    def _update_sw_traceability_enabled(self):
        isStart = self.btnStart.text() == "Start"
        if self.fixture.is_retest_mode() and not self.forceTraceabilityEnabled:
            self.swTraceability.setEnabled(False)
        else:
            self.swTraceability.setEnabled(isStart)

    def equals(self, fixture: Fixture) -> bool:
        return self.fixture.equals(fixture)

    def equalsIp(self, fixtureIp: str) -> bool:
        return self.fixture.equalsIp(fixtureIp)

    def set_fixture_isTesting(self, value: bool):
        self.fixture.set_isTesting(value)
        self.update()
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
        self.update()

    def toggle_force_traceability_enabled(self):
        self.forceTraceabilityEnabled = not self.forceTraceabilityEnabled
        self._update_sw_traceability_enabled()

    def set_lock_enabled(self, value: bool):
        self.fixture.set_lock_enabled(value)
        self._fixtureController.update(self.fixture)
        self.update()
