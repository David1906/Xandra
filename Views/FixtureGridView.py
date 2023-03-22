from Controllers.FixtureGridController import FixtureGridController
from Models.Fixture import Fixture
from Models.Test import Test
from PyQt5 import QtCore
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QShortcut
from Views.AuthView import AuthView
from Views.FixtureView import FixtureView


class FixtureGridView(QWidget):
    BOX_SPACING = 30
    ROW_NUMBER = 3
    lock_changed = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self._fixtureViews: "list[FixtureView]" = []
        self._fixtureGridController = FixtureGridController()
        self._fixtureGridController.fixture_change.connect(self.update_fixture)
        self._fixtureGridController.test_add.connect(self.on_test_add)
        self._fixtureGridController.testing_status_changed.connect(
            self.on_testing_status_changed
        )
        self._isRetestMode = False
        self._isLockEnabled = False

        self.hBox = QHBoxLayout()
        self.setLayout(self.hBox)
        self.create_fixtureViews()

        self.msgSc = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        self.msgSc.activated.connect(self.start_all_fixtures)

        self.msgSt = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        self.msgSt.activated.connect(self.stop_all_fixtures)

        self.msgSt = QShortcut(QKeySequence("Ctrl+Shift+R"), self)
        self.msgSt.activated.connect(self.show_retest_mode)
        self.msgForceTraceability = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        self.msgForceTraceability.activated.connect(
            self.toggle_force_traceability_enabled
        )

        self.msgSt = QShortcut(QKeySequence("Ctrl+Shift+L"), self)
        self.msgSt.activated.connect(self.toggle_lock_enabled_all_fixtures)

        self.set_enable_lock(True)

    def show_retest_mode(self):
        self._isRetestMode = not self._isRetestMode
        for fixtureView in self._fixtureViews:
            fixtureView.set_retest_mode_visibility(self._isRetestMode)
            fixtureView.disableRetestMode()

    def toggle_force_traceability_enabled(self):
        if not self._isRetestMode:
            return
        authView = AuthView(self)
        authView.interact()
        if authView.isAuthorized:
            for fixtureView in self._fixtureViews:
                fixtureView.toggle_force_traceability_enabled()

    def create_fixtureViews(self):
        fixtures = self._fixtureGridController.get_all_fixtures()
        for fixture in fixtures:
            self._fixtureViews.append(FixtureView(fixture))

        vBox = QVBoxLayout()
        for i in range(len(self._fixtureViews)):
            if i % FixtureGridView.ROW_NUMBER == 0:
                vBox = QVBoxLayout()
                self.hBox.addLayout(vBox)
            vBox.addWidget(self._fixtureViews[i])

    def interact(self):
        self._fixtureGridController.start_watch_logs()

    def on_testing_status_changed(self, fixtureIp: str, isTesting: bool):
        for fixtureView in self._fixtureViews:
            if fixtureView.equalsIp(fixtureIp):
                fixtureView.set_fixture_isTesting(isTesting)
                return

    def on_test_add(self, test: Test):
        for fixtureView in self._fixtureViews:
            if fixtureView.equalsIp(test.fixtureIp):
                fixtureView.set_test(test)
                return

    def start_all_fixtures(self):
        for fixtureView in self._fixtureViews:
            fixtureView.start()

    def stop_all_fixtures(self):
        for fixtureView in self._fixtureViews:
            fixtureView.stop()

    def toggle_lock_enabled_all_fixtures(self):
        authView = AuthView(self)
        authView.interact()
        if authView.isAuthorized:
            self.set_enable_lock(not self._isLockEnabled)

    def set_enable_lock(self, value: bool):
        self._isLockEnabled = value
        for fixtureView in self._fixtureViews:
            fixtureView.set_lock_enabled(self._isLockEnabled)
        self.lock_changed.emit(self._isLockEnabled)

    def update_fixture(self, fixture: Fixture):
        for fixtureView in self._fixtureViews:
            if fixtureView.equalsIp(fixture.get_ip()):
                fixtureView.set_fixture(fixture)
