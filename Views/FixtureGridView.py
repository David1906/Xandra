from Controllers.FixtureGridController import FixtureGridController
from Models.Fixture import Fixture
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
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
        self._fixtureGridController.config_change.connect(
            lambda event: self.config_change.emit(event)
        )
        self._showRetestMode = False
        self._isLockEnabled = False
        self.setStyleSheet("QLabel {font: 8pt Open Sans}")

        self.hBox = QHBoxLayout()
        self.setLayout(self.hBox)
        self.create_fixtureViews()

        self.set_enable_lock(True)

    def toggle_retest_mode(self):
        authView = AuthView(self)
        authView.interact()
        if authView.isAuthorized:
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

    def _on_test_started(self, fixtureIp: str):
        self._set_fixture_testing(fixtureIp, True)

    def _set_fixture_pre_testing(self, fixtureIp: str, isTesting: bool):
        fixtureView = self._find_fixture_view(fixtureIp)
        if fixtureView != None:
            fixtureView.set_fixture_isPreTesting(isTesting)

    def _set_fixture_testing(self, fixtureIp: str, isTesting: bool):
        fixtureView = self._find_fixture_view(fixtureIp)
        if fixtureView != None:
            fixtureView.set_fixture_isTesting(isTesting)

    def expand_all_config_panels(self):
        for fixtureView in self._fixtureViews:
            fixtureView.expand_config_panel()

    def collapse_all_config_panels(self):
        for fixtureView in self._fixtureViews:
            fixtureView.collapse_config_panel()

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

    def update_catalogs(self):
        for fixtureView in self._fixtureViews:
            fixtureView.update_catalogs()
