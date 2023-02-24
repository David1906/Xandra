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
        self.createFixtureViews()

    def createFixtureViews(self):
        fixtures = self._fixtureGridController.getAllFixtures()
        for fixture in fixtures:
            self._fixtureViews.append(FixtureView(fixture))

        vBox = QVBoxLayout()
        for i in range(len(self._fixtureViews)):
            if i % FixtureGridView.ROW_NUMBER == 0:
                vBox = QVBoxLayout()
                self.hBox.addLayout(vBox)
            vBox.addWidget(self._fixtureViews[i])

    def interact(self):
        self._fixtureGridController.updated.connect(self.updateFixture)
        self._fixtureGridController.startWatchLogs()

    def updateFixture(self, test: Test, fixture: Fixture):
        for fixtureView in self._fixtureViews:
            if fixtureView.equals(fixture):
                fixtureView.setFixture(fixture)
                fixtureView.setTest(test)
                return
