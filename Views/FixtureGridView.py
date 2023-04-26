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
    config_change = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self._fixtureViews: "list[FixtureView]" = []
        self._fixtureGridController = FixtureGridController()
        self._fixtureGridController.fixture_change.connect(self.update_fixture)
        self._fixtureGridController.test_add.connect(self.on_test_add)
        self._fixtureGridController.config_change.connect(
            lambda event: self.config_change.emit(event)
        )
        self._fixtureGridController.testing_status_changed.connect(
            self.on_testing_status_changed
        )
        self._showRetestMode = False
        self._isLockEnabled = False
        self.setStyleSheet("QLabel {font: 8pt Open Sans}")

        self.hBox = QHBoxLayout()
        self.setLayout(self.hBox)
        self.create_fixtureViews()

        self.set_enable_lock(True)

    def show_retest_mode(self):
        self._showRetestMode = not self._showRetestMode
        for fixtureView in self._fixtureViews:
            fixtureView.set_retest_mode_visibility(self._showRetestMode)

    def toggle_force_traceability_enabled(self):
        if not self._showRetestMode:
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
        fixtureView = self._find_fixture_view(fixtureIp)
        if fixtureView != None:
            fixtureView.set_fixture_isTesting(isTesting)

    def on_test_add(self, test: Test):
        fixtureView = self._find_fixture_view(test.fixtureIp)
        if fixtureView != None:
            fixtureView.add_test(test)

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
        fixtureView = self._find_fixture_view(fixture.ip)
        if fixtureView != None:
            fixtureView.copy_configs(fixture)

    def _find_fixture_view(self, fixtureIp: str):
        for fixtureView in self._fixtureViews:
            if fixtureView.equalsIp(fixtureIp):
                return fixtureView

    def save_status(self):
        for fixtureView in self._fixtureViews:
            fixtureView.save_status()
