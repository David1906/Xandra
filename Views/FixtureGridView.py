import os
from Controllers.FixtureGridController import FixtureGridController
from Models.FixtureConfig import FixtureConfig
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QShortcut
from PyQt5.QtGui import QKeySequence
from Models.Test import Test
from Views.AuthView import AuthView
from Views.FixtureView import FixtureView


class FixtureGridView(QWidget):
    BOX_SPACING = 30
    ROW_NUMBER = 3

    def __init__(self):
        super().__init__()

        self._fixtureViews: "list[FixtureView]" = []
        self._fixtureGridController = FixtureGridController()
        self._fixtureGridController.test_add.connect(self.on_test_add)
        self._fixtureGridController.testing_status_changed.connect(
            self.on_testing_status_changed
        )
        self._isRetestMode = False

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

    def show_retest_mode(self):
        self._isRetestMode = not self._isRetestMode
        for fixtureView in self._fixtureViews:
            fixtureView.set_retest_mode_visibility(self._isRetestMode)
            fixtureView.disableRetestMode()

    def toggle_force_traceability_enabled(self):
        if not self._isRetestMode:
            return
        authView = AuthView()
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
