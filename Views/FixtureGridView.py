from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from Controllers.FixtureGridController import FixtureGridController
from Models.Fixture import Fixture
from Views.FixtureView import FixtureView


class FixtureGridView(QWidget):
    BOX_SPACING = 30
    ROW_NUMBER = 3

    def __init__(self):
        super().__init__()

        self._fixtureViews = []
        self._fixtureGridController = FixtureGridController()

        self.hBox = QHBoxLayout()
        self.setLayout(self.hBox)
        self.set_fixtures(self._fixtureGridController.get_fixtures())

    def set_fixtures(self, fixtures: "list[Fixture]"):
        self.create_fixture_views(fixtures)
        for fixtureView in self._fixtureViews:
            for fixture in fixtures:
                if fixtureView.equals(fixture):
                    fixtureView.set_fixture(fixture)

    def create_fixture_views(self, fixtures: "list[Fixture]"):
        if len(self._fixtureViews) > 0:
            return

        for fixture in fixtures:
            self._fixtureViews.append(FixtureView(fixture))

        vBox = QVBoxLayout()
        for i in range(len(self._fixtureViews)):
            if i % FixtureGridView.ROW_NUMBER == 0:
                vBox = QVBoxLayout()
                self.hBox.addLayout(vBox)
            vBox.addWidget(self._fixtureViews[i])

    def interact(self):
        self._fixtureGridController.start_watch_yield(self.set_fixtures)
