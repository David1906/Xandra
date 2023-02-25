from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Utils.PathHelper import PathHelper
from Views.FixtureGridView import FixtureGridView


class MainWindow(QMainWindow):
    ICON_FULLPATH = PathHelper().get_root_path() + "/Static/icon.png"
    BOX_SPACING = 30

    def __init__(self, title: str = "Xandra - FBT"):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(MainWindow.ICON_FULLPATH))

        self.fixtureView = FixtureGridView()
        self.setCentralWidget(self.fixtureView)
        self.fixtureView.interact()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit Xandra",
            f"Are you sure to exit Xandra? It will stop all fixtures",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
