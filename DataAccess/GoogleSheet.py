from Core.Enums.FixtureStatus import FixtureStatus
from DataAccess.FixtureStatusLogDAO import FixtureStatusLogDAO
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.MaintenanceDAO import MaintenanceDAO
from DataAccess.TestDAO import TestDAO
from oauth2client.service_account import ServiceAccountCredentials
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QTimer
from typing import Callable
from typing import TypeVar
import gspread
import logging
import time

T = TypeVar("T")


class Emitter(QObject):
    status_update = pyqtSignal(str)
    done = pyqtSignal()


class GoogleSheet(QRunnable):
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
        self._isSyncing = False
        self._syncs = [self.sync_tasks, self.sync_maintenance, self.sync_status_log]
        self._currentStep = 0
        self._totalSteps = len(self._syncs)
        self.emitter = Emitter()
        self._timeoutTimer = QTimer()
        self._timeoutTimer.timeout.connect(self._stop_sync)
        self._timeoutTimer.start(GoogleSheet.EXECUTION_TIMEOUT)
        self._interrupt = False

    def _get_client(self):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self._mainConfigDAO.get_google_keyfilePath(),
            GoogleSheet.SCOPE,
        )
        client = gspread.authorize(self.credentials)
        client.set_timeout(30)
        return client

    def run(self):
        try:
            self._currentStep = 0
            for sync in self._syncs:
                self._currentStep += 1
                sync()
        except:
            pass
        self.emitter.done.emit()

    def _stop_sync(self):
        self._interrupt = True
        self.emitter.done.emit()

    def sync_tasks(self):
        self._sync_sheet(
            sheetName=self._mainConfigDAO.get_google_sheetName(),
            items=self._testDAO.find_not_sync(),
            transformer=lambda test: (
                [
                    f"{test.fixtureIp.split('.')[-1]}_{test.id}",
                    test.serialNumber,
                    test.project,
                    test.startTime.strftime("%d/%m/%Y %H:%M:%S"),
                    test.endTime.strftime("%d/%m/%Y %H:%M:%S"),
                    test.codeVersion,
                    test.fixtureIp,
                    "PASS" if test.status else "FAILED",
                    test.stepLabel,
                    test.operator,
                    test.description,
                ]
            ),
            callback=self._testDAO.update_is_sync,
        )

    def sync_maintenance(self):
        self._sync_sheet(
            sheetName=self._mainConfigDAO.get_google_maintenanceSheetName(),
            items=self._maintenanceDAO.find_not_sync(),
            transformer=lambda maintenance: (
                [
                    f"{maintenance.fixtureIp.split('.')[-1]}_{maintenance.id}",
                    maintenance.employee,
                    maintenance.fixtureIp,
                    maintenance.part,
                    maintenance.action,
                    maintenance.description,
                    f"{maintenance.fixtureIp.split('.')[-1]}_{maintenance.testId}",
                    maintenance.stepLabel,
                    "PASS" if maintenance.resultStatus else "FAILED",
                    maintenance.dateTime.strftime("%d/%m/%Y %H:%M:%S"),
                ]
            ),
            callback=self._maintenanceDAO.update_is_sync,
        )

    def sync_status_log(self):
        self._sync_sheet(
            sheetName=self._mainConfigDAO.get_google_statusLogSheetName(),
            items=self._fixtureStatusLogDAO.find_not_sync(),
            transformer=lambda fixtureStatusLogDTO: (
                [
                    f"{fixtureStatusLogDTO.fixtureIp.split('.')[-1]}_{fixtureStatusLogDTO.id}",
                    fixtureStatusLogDTO.fixtureIp,
                    FixtureStatus(fixtureStatusLogDTO.status).description,
                    fixtureStatusLogDTO.reason,
                    fixtureStatusLogDTO.seconds,
                    fixtureStatusLogDTO.timeStampStart.strftime("%d/%m/%Y %H:%M:%S"),
                    fixtureStatusLogDTO.timeStampEnd.strftime("%d/%m/%Y %H:%M:%S"),
                ]
            ),
            callback=self._fixtureStatusLogDAO.update_is_sync,
            batchSize=200,
        )

    def _sync_sheet(
        self,
        sheetName: str,
        items: "list[T]",
        transformer: Callable[[T], "list[str]"],
        callback: Callable[[T], None],
        batchSize: int = 100,
        keyNo: int = 0,
    ):
        try:
            sheet = self._get_client().open(sheetName).sheet1
            syncedItems = 0
            batchItems = items[syncedItems:batchSize]
            while len(batchItems) > 0 and not self._interrupt:
                self.emitter.status_update.emit(
                    f"({self._currentStep}/{self._totalSteps}) Syncing {sheetName} {syncedItems}/{len(items)}..."
                )

                rows = []
                for item in batchItems:
                    rows.append(transformer(item))
                sheet.append_rows(
                    rows,
                    value_input_option="USER_ENTERED",
                )

                for item in batchItems:
                    callback(item, True)
                    syncedItems += 1
                batchItems = items[syncedItems : syncedItems + batchSize]
                time.sleep(1)
        except Exception as e:
            msg = f"Error in sync {sheetName}: " + str(e)
            if "Quota exceeded" in msg and keyNo < GoogleSheet.MAX_KEY_NO:
                print("Using next key: ", keyNo + 1)
                self._sync_sheet(
                    sheetName, items, transformer, callback, batchSize, keyNo + 1
                )
            else:
                print(msg)
                logging.error(msg)
