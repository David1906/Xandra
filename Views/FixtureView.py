from Controllers.FixtureController import FixtureController
from Core.Enums.FixtureMode import FixtureMode
from Core.Enums.FixtureStatus import FixtureStatus
from datetime import datetime
from Core.Enums.TestStatus import TestStatus
from Models.Fixture import Fixture
from Models.Maintenance import Maintenance
from Models.NullTestAnalysis import NullTestAnalysis
from Models.TestAnalysis import TestAnalysis
from Models.Test import Test
from PyQt5 import QtCore, QtGui
from Utils.PathHelper import PathHelper
from Views.TempView import TempView
from Views.Terminal import Terminal
from Views.LastFailuresWindow import LastFailuresWindow
from Views.LastTestsWindow import LastTestsWindow
from Views.LedIndicator import LedIndicator
from Views.MaintenanceLogView import MaintenanceLogView
from Views.MaintenanceView import MaintenanceView
from Views.Switch import Switch
from PyQt5.QtWidgets import (
    QGroupBox,
    QLabel,
    QPushButton,
    QGridLayout,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
)
from Utils.Translator import Translator

_ = Translator().gettext
ngettext = Translator().ngettext


class FixtureView(QGroupBox):
    LABEL_STYLE = "font-size: 12px; font-weight: bold; margin: 5px"

    def __init__(self, fixture: Fixture):
        super().__init__()

        self._fixture: Fixture = fixture
        self._lastLogsWindow = None
        self._fixtureController = FixtureController()
        self.forceTraceabilityEnabled = False
        self.updateConnection = None
        self.testingTickConnection = None
        self.overElapsedConnection = None
        self.statusChangeConnection = None
        self.updateMaintenanceConnection = None
        self.lastAnalysis = NullTestAnalysis()

        self._init_ui()

        self.fixture = fixture

    def _init_ui(self):
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

        self.lblYield = QLabel(_("Yield:"))
        infoLayout.addWidget(self.lblYield, alignment=QtCore.Qt.AlignCenter)

        self.lblMode = QLabel(_("Mode:"))
        infoLayout.addWidget(self.lblMode, alignment=QtCore.Qt.AlignCenter)

        self.lblIp = QLabel(_("IP:"))
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
        self.lblTraceability = QLabel(_("Traceability"))
        traceabilityLayout.addWidget(self.lblTraceability)
        self.swTraceability = Switch()
        self.swTraceability.setChecked(self.fixture.mode != FixtureMode.OFFLINE)
        self.swTraceability.toggled.connect(self.on_swTraceability_change)
        traceabilityLayout.addWidget(
            self.swTraceability, alignment=QtCore.Qt.AlignRight
        )
        selectorsLayout.addLayout(traceabilityLayout)

        retestLayout = QHBoxLayout()
        self.lblRetestMode = QLabel(_("Retest Mode"))
        retestLayout.addWidget(self.lblRetestMode)
        self.swRetestMode = Switch()
        self.swRetestMode.toggled.connect(self.on_swRetestMode_change)
        self.set_retest_mode_visibility(False)
        retestLayout.addWidget(self.swRetestMode, alignment=QtCore.Qt.AlignRight)
        selectorsLayout.addLayout(retestLayout)

        selectorsLayout.addStretch()

        buttonsLayout = QGridLayout()
        self.btnStart = QPushButton(_("Start"))
        self.btnStart.setIcon(
            QtGui.QIcon(PathHelper().join_root_path("/Static/start.png"))
        )
        self.btnStart.setStyleSheet("font-weight: 500;")
        self.btnStart.setFixedHeight(50)
        self.btnStart.clicked.connect(self.on_btnStart_clicked)
        buttonsLayout.addWidget(self.btnStart, 0, 0, 1, 3)

        sideGridLayout.addLayout(buttonsLayout, 2, 0)
        self.btnLastTests = QPushButton()
        self.btnLastTests.setStyleSheet(
            "font-size: 12px; font-weight: 300; padding: 3px;"
        )
        self.btnLastTests.setIcon(
            QtGui.QIcon(PathHelper().join_root_path("/Static/report.png"))
        )
        self.btnLastTests.clicked.connect(self.on_btnLastTests_clicked)
        buttonsLayout.addWidget(self.btnLastTests, 1, 0, 1, 1)

        self.btnLastFailures = QPushButton()
        self.btnLastFailures.setIcon(
            QtGui.QIcon(PathHelper().join_root_path("/Static/error.png"))
        )
        self.btnLastFailures.setStyleSheet(
            "font-size: 12px; font-weight: 300; padding: 3px;"
        )
        self.btnLastFailures.clicked.connect(self.on_btnLastFailures_clicked)
        buttonsLayout.addWidget(self.btnLastFailures, 1, 1, 1, 1)

        self.btnMaintenanceLog = QPushButton()
        self.btnMaintenanceLog.setIcon(
            QtGui.QIcon(PathHelper().join_root_path("/Static/maintenance.png"))
        )
        self.btnMaintenanceLog.setStyleSheet(
            "font-size: 12px; font-weight: 300; padding: 3px;"
        )
        self.btnMaintenanceLog.clicked.connect(self.on_btnMaintenanceLog_clicked)
        buttonsLayout.addWidget(self.btnMaintenanceLog, 1, 2, 1, 1)

        self.terminal = Terminal(
            self.fixture.id, self._fixtureController.get_automatic_product_selection()
        )
        self.terminal.finished.connect(self._on_terminal_finished)
        self.terminal.change.connect(self.on_terminal_change)
        if self.terminal.has_tmux_session():
            # TODO fix terminal size self.start()
            pass
        gridLayout.addWidget(self.terminal, 0, 0, 2, 1)

        self.maintenanceView = MaintenanceView(
            self,
            self.fixture.id,
            self.fixture.ip,
            items=self._fixtureController.get_maintenance_parts(),
            actions=self._fixtureController.get_maintenance_actions(),
        )
        self.maintenanceView.selected.connect(self._on_maintenance_selected)
        gridLayout.addWidget(self.maintenanceView, 0, 0, 1, 1)

        self.lblResult = QLabel(_("Status: IDLE"))
        self.lblResult.setStyleSheet(FixtureView.LABEL_STYLE)
        gridLayout.addWidget(
            self.lblResult, 2, 0, 1, 1, alignment=QtCore.Qt.AlignCenter
        )

        self.tempView = TempView()
        sideFooterLayout = QHBoxLayout()
        sideFooterLayout.setContentsMargins(0, 0, 0, 0)
        sideFooterLayout.addWidget(self.tempView)
        gridLayout.addLayout(sideFooterLayout, 2, 1, 1, 1)

    def on_btnLastTests_clicked(self):
        self._lastLogsWindow = LastTestsWindow(
            self.fixture.ip, showRetest=self.swRetestMode.getChecked()
        )
        self._lastLogsWindow.showMaximized()

    def on_btnLastFailures_clicked(self):
        self._lastLogsWindow = LastFailuresWindow(
            self.fixture.ip, showRetest=self.swRetestMode.getChecked()
        )
        self._lastLogsWindow.showMaximized()

    def on_btnMaintenanceLog_clicked(self):
        self._lastLogsWindow = MaintenanceLogView(self.fixture.ip)
        self._lastLogsWindow.showMaximized()

    def on_swRetestMode_change(self, checked: bool):
        if checked and not self.swTraceability.getChecked():
            self.swTraceability.setChecked(True)
        self.update_fixture_mode()
        self.fixture.tests = self._fixtureController.find_last_tests(self.fixture)

    def on_swTraceability_change(self, checked: bool):
        self.update_fixture_mode()

    def update_fixture_mode(self):
        self.fixture.mode = self._fixtureController.calc_mode(
            self.swTraceability.getChecked(), self.swRetestMode.getChecked()
        )

    def _on_maintenance_selected(self, maintenance: Maintenance):
        self._fixtureController.add_maintenance(maintenance)
        self.fixture.maintenance = maintenance

    def add_test(self, test: Test):
        self._fixtureController.add_test(self.fixture, test)
        self.fixture.lastTest = test
        self.fixture.tests = self._fixtureController.find_last_tests(self.fixture)

    def _update(self):
        self.btnStart.setEnabled(self.fixture.can_start() or self.fixture.isStarted)
        self.swRetestMode.setEnabled(self.fixture.can_change_retest())
        self._update_texts()
        self._update_status()
        self._update_lock_indicator()
        self._update_btn_start()
        self._update_sw_traceability_enabled()
        self.maintenanceView.setVisible(self.fixture.needs_maintenance())
        self.setStyleSheet(
            f"""
            QGroupBox#fixture{{
                border-radius: 5px;
                border: 1px solid #cccccc;
                background-color: {self.fixture.get_color()};
            }}
            """
        )
        self.lblResult.setStyleSheet(FixtureView.LABEL_STYLE)
        self._fixtureController.update(self.fixture)

    def _update_texts(self):
        self.lblYield.setText(_("Yield: {0}%").format(self.fixture.get_yield()))
        self.lblIp.setText(_("Ip: {0}").format(self.fixture.ip))
        self.lblLock.setText(
            ngettext(
                "Failed last test:", "Failed last {0} tests:", self.fixture.lockFailQty
            ).format(self.fixture.lockFailQty)
        )
        self.lblMode.setText(_("Mode: {0}").format(self.fixture.mode.description))
        self.lblTraceability.setText(_("Traceability"))
        self.lblRetestMode.setText(_("Retest Mode"))
        self.btnLastTests.setToolTip(_("Last Tests"))
        self.btnLastFailures.setToolTip(_("Last Failures"))
        self.btnMaintenanceLog.setToolTip(_("Maintenance"))
        self.maintenanceView._update_texts()

    def _update_status(self):
        self.lblResult.setText(self.fixture.get_status_message())
        self.lblResult.setToolTip(
            "" if self.fixture.isTesting else self.lblResult.text()
        )

    def _on_over_elapsed(self):
        self.lblResult.setStyleSheet(FixtureView.LABEL_STYLE + "color: #c71704;")

    def _update_lock_indicator(self):
        self.lblLock.setText(self.fixture.get_lock_description())
        self.led.set_color_red()
        isVisible = self.fixture.is_locked()
        isLedOn = isVisible
        tooltipTxt = _("Fixture locked due to {0}").format(self.lblLock.text().lower())

        if self.fixture.mode == FixtureMode.OFFLINE:
            isVisible = True
            self.led.set_color_green()
            isLedOn = self.fixture.are_last_tests_pass()
            tooltipTxt = _("Fixture unlocked")
            if not isLedOn:
                remainingToUnlock = self.fixture.get_remaining_to_unlock()
                self.lblLock.setText(_("Test {0} to unlock").format(remainingToUnlock))
                tooltipTxt = ngettext(
                    "Test another board", "Test another {0} boards", remainingToUnlock
                ).format(remainingToUnlock)
                tooltipTxt += _(" which result is pass to unlock the fixture")

        self.lblLock.setHidden(not isVisible)
        self.lblLock.setToolTip(tooltipTxt)
        self.led.setToolTip(tooltipTxt)
        self.led.setHidden(not isVisible)
        self.led.setChecked(isLedOn)

    def on_btnStart_clicked(self):
        if self.fixture.isStarted:
            reply = QMessageBox.question(
                self,
                _("Stop Fixture"),
                _("Are you sure to stop fixture {0}?").format(self.fixture.ip),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.terminal.Stop()
                self.tempView.pause()
                self.fixture.isStarted = False
        else:
            cmd = self._fixtureController.get_fct_host_cmd(
                self.fixture, self.swTraceability.getChecked()
            )
            print(cmd)
            self.terminal.start([cmd])
            self.fixture.isStarted = True

    def _update_btn_start(self):
        text = _("Start")
        if self.fixture.isStarted:
            text = _("Stop")
        self.btnStart.setText(text)
        self.btnStart.setIcon(
            QtGui.QIcon(
                PathHelper().join_root_path(
                    f"/Static/{'stop' if self.fixture.isStarted else 'start'}.png"
                )
            )
        )

    def _on_terminal_finished(self, exitStatus):
        self.fixture.isStarted = False
        self.fixture.isTesting = False
        self.lastAnalysis = NullTestAnalysis()

    def on_terminal_change(self, testAnalysis: TestAnalysis):
        if self.lastAnalysis.equals(testAnalysis):
            return
        self.lastAnalysis = testAnalysis
        if testAnalysis.has_bmc_ip() and not self.tempView.is_started():
            self.tempView.start(
                self._fixtureController.get_fct_host_control_tool_path(),
                testAnalysis.bmcIp,
            )
        self._update_by_test_analysis(testAnalysis)

    def _update_by_test_analysis(self, testAnalysis: TestAnalysis):
        if testAnalysis.status == TestStatus.Recovered:
            self.fixture.testTimer = testAnalysis.startDateTime
        if testAnalysis.is_finished():
            test = self._fixtureController.parse_test(testAnalysis)
            self.add_test(test)
            self.tempView.pause()
        elif testAnalysis.is_testing():
            self.fixture.testItem = testAnalysis.stepLabel
            self.fixture.serialNumber = testAnalysis.stepLabel
        self.fixture.isTesting = testAnalysis.is_testing()

    def save_status(self):
        self.fixture.emit_status_change(force=True)

    def _on_status_change(
        self,
        lastStatus: FixtureStatus,
        startDateTime: datetime,
        timeDelta: datetime,
        newStatus: FixtureStatus,
    ):
        self._fixtureController.add_status_log(
            self.fixture, lastStatus, startDateTime, timeDelta
        )

    def _on_update_maintenance(
        self,
        maintenance: Maintenance,
    ):
        self._fixtureController.update_maintenance(maintenance)

    def _update_sw_traceability_enabled(self):
        isEnabled = self.fixture.can_change_traceability()
        if self.forceTraceabilityEnabled:
            isEnabled = not self.fixture.isStarted
        self.swTraceability.setEnabled(isEnabled)

    def equals(self, fixture: Fixture) -> bool:
        return self.fixture.equals(fixture)

    def equalsIp(self, fixtureIp: str) -> bool:
        return self.fixture.equalsIp(fixtureIp)

    def set_fixture_isTesting(self, value: bool):
        self.fixture.isPreTesting = False
        self.fixture.isTesting = value

    def set_fixture_isPreTesting(self, value: bool):
        self.fixture.isPreTesting = value

    def start(self):
        if not self.fixture.isStarted and not self.fixture.is_locked():
            self.on_btnStart_clicked()

    def stop(self):
        if self.fixture.isStarted:
            self.on_btnStart_clicked()

    def set_retest_mode_visibility(self, value):
        if value:
            self.lblRetestMode.show()
            self.swRetestMode.show()
        else:
            self.lblRetestMode.hide()
            self.swRetestMode.hide()
        self.swRetestMode.setChecked(False)

    def toggle_force_traceability_enabled(self):
        self.forceTraceabilityEnabled = not self.forceTraceabilityEnabled
        self._update_sw_traceability_enabled()

    def set_lock_enabled(self, value: bool):
        self.fixture.isLockEnabled = value

    def copy_configs(self, fixture: Fixture):
        self.fixture.copy_configs(fixture)
        self.update_catalogs()

    @property
    def fixture(self) -> Fixture:
        return self._fixture

    @fixture.setter
    def fixture(self, fixture: Fixture):
        if self.updateConnection:
            self.fixture.update.disconnect(self.updateConnection)
        if self.testingTickConnection:
            self.fixture.testing_tick.disconnect(self.testingTickConnection)
        if self.overElapsedConnection:
            self.fixture.over_elapsed.disconnect(self.overElapsedConnection)
        if self.statusChangeConnection:
            self.fixture.status_change.disconnect(self.statusChangeConnection)
        if self.updateMaintenanceConnection:
            self.fixture.update_maintenance.disconnect(self.updateMaintenanceConnection)
        self.updateConnection = fixture.update.connect(self._update)
        self.testingTickConnection = fixture.testing_tick.connect(self._update_status)
        self.overElapsedConnection = fixture.over_elapsed.connect(self._on_over_elapsed)
        self.updateMaintenanceConnection = fixture.update_maintenance.connect(
            self._on_update_maintenance
        )
        self.statusChangeConnection = fixture.status_change.connect(
            self._on_status_change
        )
        self._fixture = fixture
        self.maintenanceView.fixtureId = fixture.id
        self.maintenanceView.fixtureIp = fixture.ip

    def update_catalogs(self):
        self.maintenanceView.items = self._fixtureController.get_maintenance_parts()
        self.maintenanceView.actions = self._fixtureController.get_maintenance_actions()
