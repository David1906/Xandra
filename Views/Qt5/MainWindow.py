from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow
from Views.Qt5.FixtureGridView import FixtureGridView


class MainWindow(QMainWindow):
    ICON_FULLPATH = "./Resources/icon.png"
    BOX_SPACING = 30

    def __init__(self, title="Xandra - FBT"):
        super().__init__()

        self.setWindowTitle(title)

        self.fixtureView = FixtureGridView()
        self.setCentralWidget(self.fixtureView)
