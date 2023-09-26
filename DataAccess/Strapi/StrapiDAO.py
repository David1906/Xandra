from Core.Enums.FixtureStatus import FixtureStatus
from DataAccess.CatalogItemDAO import CatalogItemDAO
from DataAccess.EmployeeDAO import EmployeeDAO
from DataAccess.FixtureStatusLogDAO import FixtureStatusLogDAO
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.MaintenanceDAO import MaintenanceDAO
from DataAccess.SettingDAO import SettingDAO
from DataAccess.Strapi.ActionCatalogDAO import ActionCatalogDAO
from DataAccess.Strapi.CatalogDAO import CatalogDAO
from DataAccess.Strapi.EmployeeDAO import EmployeeDAO as StrapiEmployeeDAO
from DataAccess.Strapi.SparePartCatalogDAO import SparePartCatalogDAO
from DataAccess.Strapi.StrapiApi import StrapiApi
from DataAccess.TestDAO import TestDAO
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QTimer
from typing import Callable
from typing import TypeVar
from Utils.Translator import Translator
import logging
import time

_ = Translator().gettext
T = TypeVar("T")


class Emitter(QObject):
    status_update = pyqtSignal(str)
    catalogs_updated = pyqtSignal()
    done = pyqtSignal(bool)


class StrapiDAO(QRunnable):
    EXECUTION_TIMEOUT = 60000
    MAX_KEY_NO = 4
    SCOPE = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    status_update = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self._testDAO = TestDAO()
        self._fixtureStatusLogDAO = FixtureStatusLogDAO()
        self._maintenanceDAO = MaintenanceDAO()
        self._mainConfigDAO = MainConfigDAO()
        self._settingsDAO = SettingDAO()
        self._employeeDAO = EmployeeDAO()
        self._catalogItemDAO = CatalogItemDAO()
        self.emitter = Emitter()
        self._actionCatalogDAO = ActionCatalogDAO(self._settingsDAO)
        self._sparePartCatalogDAO = SparePartCatalogDAO(self._settingsDAO)
        self._strapiEmployeeDAO = StrapiEmployeeDAO(self._settingsDAO)
        self._isSyncing = False
        self._syncs = [
            self._sync_catalogs,
            self._sync_employees,
            self.sync_tests,
            self.sync_maintenance,
            self.sync_status_log,
        ]
        self._currentStep = 0
        self._totalSteps = len(self._syncs)

        self._timeoutTimer = QTimer()
        self._timeoutTimer.timeout.connect(self._stop_sync)
        self._timeoutTimer.start(StrapiDAO.EXECUTION_TIMEOUT)
        self._interrupt = False

    def run(self):
        self._currentStep = 0
        isSuccess = True
        for sync in self._syncs:
            self._currentStep += 1
            try:
                sync()
            except Exception as e:
                msg = f"Error in run StrapiDAO: " + str(e)
                print(msg)
                logging.error(msg)
                isSuccess = False
        self.emitter.done.emit(isSuccess)

    def _stop_sync(self):
        self._interrupt = True
        self.emitter.done.emit(True)

    def sync_tests(self):
        iso_date = self.get_iso_date()
        self._sync_table(
            tableName=_("tests"),
            items=self._testDAO.find_not_sync(),
            transformer=lambda test: (
                {
                    "testId": f"{test.fixtureIp.split('.')[-1]}_{test.id}",
                    "serialNumber": test.serialNumber,
                    "project": test.project,
                    "startTime": test.startTime.isoformat(),
                    "endTime": test.endTime.isoformat(),
                    "codeVersion": test.codeVersion,
                    "ip": test.fixtureIp,
                    "status": "PASS" if test.status else "FAILED",
                    "stepLabel": test.stepLabel,
                    "operator": test.operator,
                    "errorInfo": test.description,
                    "createdAt": iso_date,
                    "updatedAt": iso_date,
                    "publishedAt": iso_date,
                }
            ),
            callback=self._testDAO.bulk_update_is_sync,
        )

    def sync_maintenance(self):
        iso_date = self.get_iso_date()
        self._sync_table(
            tableName=_("maintenances"),
            items=self._maintenanceDAO.find_not_sync(),
            transformer=lambda maintenance: (
                {
                    "maintenanceId": f"{maintenance.fixtureIp.split('.')[-1]}_{maintenance.id}",
                    "employee": maintenance.employee,
                    "fixtureIp": maintenance.fixtureIp,
                    "part": maintenance.part,
                    "action": maintenance.action,
                    "comment": maintenance.description,
                    "testId": f"{maintenance.fixtureIp.split('.')[-1]}_{maintenance.testId}",
                    "step_label": maintenance.stepLabel,
                    "testResult": "PASS" if maintenance.resultStatus else "FAILED",
                    "timeStamp": maintenance.dateTime.isoformat(),
                    "createdAt": iso_date,
                    "updatedAt": iso_date,
                    "publishedAt": iso_date,
                }
            ),
            callback=self._maintenanceDAO.bulk_update_is_sync,
        )

    def sync_status_log(self):
        iso_date = self.get_iso_date()
        self._sync_table(
            tableName="status-logs",
            items=self._fixtureStatusLogDAO.find_not_sync(),
            transformer=lambda fixtureStatusLogDTO: (
                {
                    "statusLogId": f"{fixtureStatusLogDTO.fixtureIp.split('.')[-1]}_{fixtureStatusLogDTO.id}",
                    "fixtureIp": fixtureStatusLogDTO.fixtureIp,
                    "status": FixtureStatus(fixtureStatusLogDTO.status).description,
                    "reason": fixtureStatusLogDTO.reason,
                    "seconds": fixtureStatusLogDTO.seconds,
                    "start": fixtureStatusLogDTO.timeStampStart.isoformat(),
                    "end": fixtureStatusLogDTO.timeStampEnd.isoformat(),
                    "createdAt": iso_date,
                    "updatedAt": iso_date,
                    "publishedAt": iso_date,
                }
            ),
            callback=self._fixtureStatusLogDAO.bulk_update_is_sync,
            batchSize=100,
        )

    def get_iso_date(self):
        today = datetime.now()
        return today.isoformat()

    def _sync_table(
        self,
        tableName: str,
        items: "list[T]",
        transformer: Callable[[T], "list[str]"],
        callback: Callable[["list[T]"], None],
        batchSize: int = 50,
    ):
        try:
            syncedItems = 0
            batchItems = items[syncedItems:batchSize]
            while len(batchItems) > 0 and not self._interrupt:
                txtSync = _("Syncing")
                self.emitter.status_update.emit(
                    f"({self._currentStep}/{self._totalSteps}) {txtSync} {tableName} {syncedItems}/{len(items)}..."
                )

                rows = []
                for item in batchItems:
                    rows.append(transformer(item))
                StrapiApi(self._mainConfigDAO.get_sync_server()).post(
                    f"/{tableName[:-1]}/bulk", rows
                )

                callback(batchItems, True)
                syncedItems += len(batchItems)
                batchItems = items[syncedItems : syncedItems + batchSize]
                time.sleep(1)
        except Exception as e:
            msg = f"Error in sync {tableName}: " + str(e)
            print(msg)
            logging.error(msg)

    def _sync_employees(self):
        if not self._strapiEmployeeDAO.should_sync():
            return
        self._emit_syncing_status_update(self._strapiEmployeeDAO.group)
        self._strapiEmployeeDAO.sync()

    def _sync_catalogs(self):
        catalogDAO: CatalogDAO
        for catalogDAO in [self._actionCatalogDAO, self._sparePartCatalogDAO]:
            if catalogDAO.should_sync():
                self._emit_syncing_status_update(catalogDAO.group)
                catalogDAO.sync()
                self.emitter.catalogs_updated.emit()

    def _emit_syncing_status_update(self, step: str):
        self._emit_status_update(_("Syncing") + f" {_(step)}...")

    def _emit_status_update(self, msg: str):
        self.emitter.status_update.emit(
            f"({self._currentStep}/{self._totalSteps}) {msg}"
        )
