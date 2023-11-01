import sys
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.Strapi.StrapiDAO import StrapiDAO
from datetime import datetime
from Products.HostControlBuilder import HostControlBuilder
from PyQt5 import QtGui, QtCore, QtWidgets
from Utils.HttpServer import HttpServer
from Utils.PathHelper import PathHelper
from Utils.Translator import Translator
from Views.FixtureGridView import FixtureGridView
import os
import random
import subprocess
from PyQt5.QtWidgets import (
    QAction,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QWidget,
)

_ = Translator().gettext


class MainWindow(QMainWindow):
    ICON_FULLPATH = PathHelper().get_root_path() + "/Static/icon.png"
    BOX_SPACING = 30

    def __init__(self, title: str = "Xandra - FBT"):
        super().__init__()

        self.isLockEnabled = True
        self._hostControl = HostControlBuilder().build_based_on_main_config()
        self._mainConfigDAO = MainConfigDAO()
        self._isSyncing = False

        self.setWindowTitle(title)
        self._init_ui()
        self._create_actions()
        self._add_actions()
        self._create_menus()
        self._update_texts()

        self._hostControl.initialize()

        self._syncTimer = QtCore.QTimer()
        self._syncTimer.timeout.connect(self._sync_all_async)
        self._update_sync_timer()

        self._httpServer = HttpServer(self)
        self._httpServer.start()
        self._httpServer.setPriority(QtCore.QThread.Priority.HighestPriority)

    def _init_ui(self):
        self.setWindowIcon(QtGui.QIcon(MainWindow.ICON_FULLPATH))

        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)

        self.fixtureGridView = FixtureGridView()
        self.fixtureGridView.lock_changed.connect(self._on_lock_changed)
        self.fixtureGridView.config_change.connect(lambda event: self._update_texts())
        gridLayout.addWidget(self.fixtureGridView, 0, 0, 99, 0)

        self.footer = QHBoxLayout()
        self.footer.setContentsMargins(15, 0, 15, 15)
        self.footer.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.lblXandraVersion = QLabel()
        self.footer.addWidget(self.lblXandraVersion, alignment=QtCore.Qt.AlignLeft)

        self.lblStatus = QLabel()
        self.footer.addWidget(self.lblStatus, alignment=QtCore.Qt.AlignCenter)

        self.lblScriptVersion = QLabel()
        self.footer.addWidget(self.lblScriptVersion, alignment=QtCore.Qt.AlignRight)
        gridLayout.addLayout(self.footer, 100, 0, alignment=QtCore.Qt.AlignBottom)

        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(gridLayout)
        self.setCentralWidget(widget)

    def _update_texts(self):
        self._update_ui_texts()
        self._update_menus_texts()
        self._update_actions_texts()

    def _update_ui_texts(self):
        self.lblXandraVersion.setText(
            _("Xandra Version: {0}").format(os.environ.get("XANDRA_VERSION"))
        )
        self.lblScriptVersion.setText(
            _("Script Version: {0}").format(self._hostControl.get_script_version())
        )
        self.lblXandraVersion.setToolTip(
            _("Developed by David Ascencio and Omar Ascencio @Foxconn")
        )

    def _add_actions(self):
        self.addAction(self.toggleRetestAction)
        self.addAction(self.toggleEnabledTracebilityAction)

    def _create_actions(self):
        self.exitAction = QAction(_("&Exit"), self)
        self.exitAction.triggered.connect(self.close)

        self.startAllAction = QAction(_("Start &All Fixtures"), self)
        self.startAllAction.setShortcut("Ctrl+Shift+A")
        self.startAllAction.triggered.connect(self.fixtureGridView.start_all_fixtures)

        self.stopAllAction = QAction(_("&Stop All Fixtures"), self)
        self.stopAllAction.setShortcut("Ctrl+Shift+S")
        self.stopAllAction.triggered.connect(self.fixtureGridView.stop_all_fixtures)

        self.toggleRetestAction = QAction(_("Toggle &Retest Mode"), self)
        self.toggleRetestAction.setShortcut("Ctrl+Shift+G")
        self.toggleRetestAction.triggered.connect(
            self.fixtureGridView.toggle_retest_mode
        )

        self.toggleEnabledTracebilityAction = QAction(
            _("Toggle &Traceablity Enabled"), self
        )
        self.toggleEnabledTracebilityAction.setShortcut("Ctrl+Shift+T")
        self.toggleEnabledTracebilityAction.triggered.connect(
            self.fixtureGridView.toggle_force_traceability_enabled
        )

        self.toggleLockAction = QAction(_("Toggle &Lock Enabled"), self)
        self.toggleLockAction.setShortcut("Ctrl+Shift+L")
        self.toggleLockAction.triggered.connect(
            self.fixtureGridView.toggle_lock_enabled_all_fixtures
        )

        self.openDocsAction = QAction(_("Open &Docs"), self)
        self.openDocsAction.setShortcut("Ctrl+Shift+D")
        self.openDocsAction.triggered.connect(self._launch_help)

        self.syncAction = QAction(_("Sync w&ith server"), self)
        self.syncAction.setShortcut("Ctrl+Shift+I")
        self.syncAction.triggered.connect(self._sync_all_async)

    def _update_actions_texts(self):
        self.exitAction.setText(_("&Exit"))
        self.startAllAction.setText(_("Start &All Fixtures"))
        self.stopAllAction.setText(_("&Stop All Fixtures"))
        self.toggleRetestAction.setText(_("Toggle &Retest Mode"))
        self.toggleEnabledTracebilityAction.setText(_("Toggle &Traceablity Enabled"))
        self.toggleLockAction.setText(_("Toggle &Lock Enabled"))
        self.openDocsAction.setText(_("Open &Docs"))

    def _create_menus(self):
        menuBar = self.menuBar()

        self.fileMenu = menuBar.addMenu(_("&File"))
        self.fileMenu.addAction(self.syncAction)
        self.fileMenu.addAction(self.exitAction)

        self.editMenu = menuBar.addMenu(_("&Run"))
        self.editMenu.addAction(self.startAllAction)
        self.editMenu.addAction(self.stopAllAction)
        self.editMenu.addAction(self.toggleLockAction)

        self.helpMenu = menuBar.addMenu(_("&Help"))
        self.helpMenu.addAction(self.openDocsAction)

    def _update_menus_texts(self):
        self.fileMenu.setTitle(_("&File"))
        self.editMenu.setTitle(_("&Run"))
        self.helpMenu.setTitle(_("&Help"))

    def _update_sync_timer(self):
        if self._mainConfigDAO.get_sync_is_activated():
            self._sync_all_async()
            self._syncTimer.start(
                self._mainConfigDAO.get_sync_interval() + random.randint(3600, 7200)
            )
        else:
            self._syncTimer.stop()

    def _sync_all_async(self):
        if not self._isSyncing:
            self._isSyncing = True
            syncDAO = StrapiDAO()
            syncDAO.emitter.status_update.connect(self._on_sync_status_update)
            syncDAO.emitter.done.connect(self._on_sync_done)
            syncDAO.emitter.catalogs_updated.connect(self._on_catalogs_updated)
            pool = QtCore.QThreadPool.globalInstance()
            pool.start(syncDAO)

    def _on_sync_done(self, isSuccess: bool):
        self._isSyncing = False
        msg = "Error"
        if isSuccess:
            msg = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self._set_status_text(_("Last sync: {0}").format(msg))

    def _on_catalogs_updated(self):
        self.fixtureGridView.update_catalogs()

    def _on_sync_status_update(self, status: str):
        self._set_status_text(status)

    def _on_lock_changed(self, value: bool):
        self.isLockEnabled = value
        self._set_status_text()

    def _set_status_text(self, status: str = None):
        allStatus = []
        if not self.isLockEnabled:
            allStatus.append(_("Lock Disabled"))
        if status != None:
            allStatus.append(status)
        txt = " - ".join(allStatus)
        self.lblStatus.setText(txt if len(txt) > 0 else " ")

    def _launch_help(self):
        subprocess.call(["bash", "-ic", "xandra-docs &"])

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            _("Exit Xandra"),
            _("Are you sure to exit Xandra?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.fixtureGridView.save_status()
            QtWidgets.QApplication.closeAllWindows()
            self._httpServer.stop()
            event.accept()
            sys.exit(0)
        else:
            event.ignore()
