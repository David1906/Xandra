from Controllers.FixtureGridController import FixtureGridController
from Models.Fixture import Fixture
from Models.Test import Test
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QShortcut, QMessageBox
from PyQt5.QtGui import QKeySequence
from Views.FixtureView import FixtureView


class FixtureGridView(QWidget):
    BOX_SPACING = 30
    ROW_NUMBER = 3

    def __init__(self):
        super().__init__()

        self._fixtureViews: "list[FixtureView]" = []
        self._fixtureGridController = FixtureGridController()
        self._fixtureGridController.updated.connect(self.update_fixture)
        self._fixtureGridController.testing_status_changed.connect(
            self.on_testing_status_changed)

        self.hBox = QHBoxLayout()
        self.setLayout(self.hBox)
        self.create_fixtureViews()

        self.msgSc = QShortcut(QKeySequence('Ctrl+Shift+A'), self)
        self.msgSc.activated.connect(self.start_all_fixtures)

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

    def update_fixture(self, fixture: Fixture):
        for fixtureView in self._fixtureViews:
            if fixtureView.equals(fixture):
                fixtureView.set_fixture(fixture)
                return

    def start_all_fixtures(self):
        for fixtureView in self._fixtureViews:
            fixtureView.start()
