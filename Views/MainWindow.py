import random
from DataAccess.FctHostControlDAO import FctHostControlDAO
from DataAccess.GoogleSheet import GoogleSheet
from DataAccess.MainConfigDAO import MainConfigDAO
from datetime import datetime
from PyQt5 import QtGui, QtCore, QtWidgets
from Utils.PathHelper import PathHelper
from Views.FixtureGridView import FixtureGridView
import os
from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QMessageBox,
    QHBoxLayout,
    QGridLayout,
    QLabel,
)


class MainWindow(QMainWindow):
    ICON_FULLPATH = PathHelper().get_root_path() + "/Static/icon.png"
    BOX_SPACING = 30

    def __init__(self, title: str = "Xandra - FBT"):
        super().__init__()

        self.isLockEnabled = True
        self._fctHostControlDAO = FctHostControlDAO()
        self._mainConfigDAO = MainConfigDAO()
        self._isSyncing = False

        self.setWindowTitle(title)
        self._init_ui()

        self._fctHostControlDAO.write_check_station_config()
        self._fctHostControlDAO.write_test_end_call_config()

        self._syncTimer = QtCore.QTimer()
        self._syncTimer.timeout.connect(self._sync_all_async)
        self._update_sync_timer()

    def _init_ui(self):
        self.setWindowIcon(QtGui.QIcon(MainWindow.ICON_FULLPATH))

        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)

        self.fixtureView = FixtureGridView()
        self.fixtureView.lock_changed.connect(self._on_lock_changed)
        gridLayout.addWidget(self.fixtureView, 0, 0, 99, 0)

        self.footer = QHBoxLayout()
        self.footer.setContentsMargins(15, 0, 15, 15)
        self.footer.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.lblXandraVersion = QLabel(
            f"Xandra Version: {os.environ.get('XANDRA_VERSION')}"
        )
        self.lblXandraVersion.setToolTip("Developed by David Ascencio\nFoxconn")
        self.footer.addWidget(self.lblXandraVersion, alignment=QtCore.Qt.AlignLeft)

        self.lblStatus = QLabel()
        self.footer.addWidget(self.lblStatus, alignment=QtCore.Qt.AlignCenter)

        self.lblScriptVersion = QLabel(
            f"Script Version: {self._fctHostControlDAO.get_script_version()}"
        )
        self.footer.addWidget(self.lblScriptVersion, alignment=QtCore.Qt.AlignRight)
        gridLayout.addLayout(self.footer, 100, 0, alignment=QtCore.Qt.AlignBottom)

        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(gridLayout)
        self.setCentralWidget(widget)
        self.fixtureView.interact()

    def _update_sync_timer(self):
        if self._mainConfigDAO.get_google_isActivated():
            self._sync_all_async()
            self._syncTimer.start(self._mainConfigDAO.get_google_syncInterval() + random.randint(3600, 7200))
        else:
            self._syncTimer.stop()

    def _sync_all_async(self):
        if not self._isSyncing:
            self._isSyncing = True
            googleSheet = GoogleSheet()
            googleSheet.emitter.status_update.connect(self._on_sync_status_update)
            googleSheet.emitter.done.connect(self._on_sync_done)
            pool = QtCore.QThreadPool.globalInstance()
            pool.start(googleSheet)

    def _on_sync_done(self):
        self._isSyncing = False
        self._set_status_text(
            f"Last sync: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )

    def _on_sync_status_update(self, status: str):
        self._set_status_text(status)

    def _on_lock_changed(self, value: bool):
        self.isLockEnabled = value
        self._set_status_text()

    def _set_status_text(self, status: str = None):
        allStatus = []
        if not self.isLockEnabled:
            allStatus.append("Lock Disabled")
        if status != None:
            allStatus.append(status)
        self.lblStatus.setText(" - ".join(allStatus))

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit Xandra",
            f"Are you sure to exit Xandra? It will stop all fixtures",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.fixtureView.save_status()
            QtWidgets.QApplication.closeAllWindows()
            event.accept()
        else:
            event.ignore()
