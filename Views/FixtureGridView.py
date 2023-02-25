from Controllers.FixtureGridController import FixtureGridController
from Models.Fixture import Fixture
from Models.Test import Test
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from Views.FixtureView import FixtureView


class FixtureGridView(QWidget):
    BOX_SPACING = 30
    ROW_NUMBER = 3

    def __init__(self):
        super().__init__()

        self._fixtureViews: "list[FixtureView]" = []
        self._fixtureGridController = FixtureGridController()

        self.hBox = QHBoxLayout()
        self.setLayout(self.hBox)
        self.create_fixtureViews()

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
        self._fixtureGridController.updated.connect(self.update_fixture)
        self._fixtureGridController.configUpdated.connect(self.update_all)
        self._fixtureGridController.start_watch_logs()

    def update_all(self, event):
        for fixture in self._fixtureGridController.get_all_fixtures():
            self.update_fixture(fixture)

    def update_fixture(self, fixture: Fixture):
        for fixtureView in self._fixtureViews:
            if fixtureView.equals(fixture):
                fixtureView.set_fixture(fixture)
                return
