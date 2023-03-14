import os
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QMessageBox,
    QHBoxLayout,
    QGridLayout,
    QLabel,
)
from DataAccess.FctHostControlData import FctHostControlData
from Utils.PathHelper import PathHelper
from Views.FixtureGridView import FixtureGridView


class MainWindow(QMainWindow):
    ICON_FULLPATH = PathHelper().get_root_path() + "/Static/icon.png"
    BOX_SPACING = 30

    def __init__(self, title: str = "Xandra - FBT"):
        super().__init__()

        self._fctHostControlData = FctHostControlData()

        self._fctHostControlData.write_check_station_config()
        self._fctHostControlData.write_test_end_call_config()

        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(MainWindow.ICON_FULLPATH))

        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)

        self.fixtureView = FixtureGridView()
        gridLayout.addWidget(self.fixtureView, 0, 0, 99, 0)

        self.footer = QHBoxLayout()
        self.footer.setContentsMargins(15, 0, 15, 15)
        self.footer.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.lblXandraVersion = QLabel(
            f"Xandra Version: {os.environ.get('XANDRA_VERSION')}"
        )
        self.footer.addWidget(self.lblXandraVersion, alignment=QtCore.Qt.AlignLeft)
        self.lblScriptVersion = QLabel(
            f"Script Version: {self._fctHostControlData.get_script_version()}"
        )
        self.footer.addWidget(self.lblScriptVersion, alignment=QtCore.Qt.AlignRight)
        gridLayout.addLayout(self.footer, 100, 0, alignment=QtCore.Qt.AlignBottom)

        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(gridLayout)
        self.setCentralWidget(widget)
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
            QtWidgets.QApplication.closeAllWindows()
            event.accept()
        else:
            event.ignore()
