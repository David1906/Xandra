from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow
from Views.FixtureGridView import FixtureGridView


class MainWindow(QMainWindow):
    ICON_FULLPATH = "./Resources/icon.png"
    BOX_SPACING = 30

    def __init__(self, title: str = "Xandra - FBT"):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(MainWindow.ICON_FULLPATH))

        self.fixtureView = FixtureGridView()
        self.setCentralWidget(self.fixtureView)
        self.fixtureView.interact()
