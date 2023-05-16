from Core.Enums.FixtureStatus import FixtureStatus
from Core.Enums.SettingType import SettingType
from DataAccess.CatalogItemDAO import CatalogItemDAO
from DataAccess.EmployeeDAO import EmployeeDAO
from DataAccess.FixtureStatusLogDAO import FixtureStatusLogDAO
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.MaintenanceDAO import MaintenanceDAO
from DataAccess.SettingDAO import SettingDAO
from DataAccess.TestDAO import TestDAO
from oauth2client.service_account import ServiceAccountCredentials
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QTimer
from typing import Callable
from typing import TypeVar
import gspread
import logging
import time
from Models.CatalogItem import CatalogItem
from Models.Employee import Employee
from Utils.Translator import Translator

_ = Translator().gettext

T = TypeVar("T")


class Emitter(QObject):
    status_update = pyqtSignal(str)
    catalogs_updated = pyqtSignal()
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
        self._settingsDAO = SettingDAO()
        self._employeeDAO = EmployeeDAO()
        self._catalogItemDAO = CatalogItemDAO()
        self._isSyncing = False
        self._syncs = [
            self._sync_lists,
            self._sync_employees,
            self.sync_tasks,
            self.sync_maintenance,
            self.sync_status_log,
        ]
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
        self._currentStep = 0
        for sync in self._syncs:
            self._currentStep += 1
            try:
                sync()
            except Exception as e:
                msg = f"Error in run GoogleSheet: " + str(e)
                print(msg)
                logging.error(msg)
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
            callback=self._testDAO.bulk_update_is_sync,
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
            callback=self._maintenanceDAO.bulk_update_is_sync,
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
            callback=self._fixtureStatusLogDAO.bulk_update_is_sync,
            batchSize=200,
        )

    def _sync_sheet(
        self,
        sheetName: str,
        items: "list[T]",
        transformer: Callable[[T], "list[str]"],
        callback: Callable[["list[T]"], None],
        batchSize: int = 100,
        keyNo: int = 0,
    ):
        try:
            sheet = self._get_client().open(sheetName).sheet1
            syncedItems = 0
            batchItems = items[syncedItems:batchSize]
            while len(batchItems) > 0 and not self._interrupt:
                txtSync = _("Syncing")
                self.emitter.status_update.emit(
                    f"({self._currentStep}/{self._totalSteps}) {txtSync} {sheetName} {syncedItems}/{len(items)}..."
                )

                rows = []
                for item in batchItems:
                    rows.append(transformer(item))
                sheet.append_rows(
                    rows,
                    value_input_option="USER_ENTERED",
                )

                callback(batchItems, True)
                syncedItems += len(batchItems)
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

    def _sync_employees(self):
        self.emitter.status_update.emit(
            f"({self._currentStep}/{self._totalSteps}) " + _("Syncing employees...")
        )
        sheetName = self._mainConfigDAO.get_google_usersSheetName()
        sheet = self._get_client().open(sheetName).sheet1
        cloudEmployeeMD5 = sheet.cell(1, 2).value
        employeeMD5Setting = self._settingsDAO.find_by_type(SettingType.EMPLOYEES_MD5)

        if cloudEmployeeMD5 == employeeMD5Setting.text:
            return

        rows = sheet.batch_get(("A3:D", "B2:B", "C2:C"))[0]
        employees = self._extract_employees(rows)

        self._employeeDAO.truncate()
        self._employeeDAO.bulk_add(employees)

        employeeMD5Setting.text = cloudEmployeeMD5
        self._settingsDAO.add_or_update(employeeMD5Setting)

    def _extract_employees(self, rows: "list[list[any]]"):
        employees: "list[Employee]" = []
        for row in rows:
            number, name, password, *unused = row
            if number.isdecimal():
                employees.append(
                    Employee(
                        number=int(number),
                        name=str(name),
                        password=str(password),
                    )
                )
        return employees

    def _sync_lists(self):
        self.emitter.status_update.emit(
            f"({self._currentStep}/{self._totalSteps}) " + _("Syncing lists...")
        )
        sheetName = self._mainConfigDAO.get_google_listsSheetName()
        sheet = self._get_client().open(sheetName).sheet1
        cloudListsMD5 = sheet.cell(1, 2).value
        listsMD5Setting = self._settingsDAO.find_by_type(SettingType.LISTS_MD5)

        if cloudListsMD5 == listsMD5Setting.text:
            return

        headersRange, catalogItemsRange = sheet.batch_get(("A2:B2", "A3:C"))
        headers = headersRange[0]

        catalogItems = []
        for headerIdx in range(0, len(headers)):
            for catalogItemsRow in catalogItemsRange:
                if catalogItemsRow[headerIdx] != "":
                    catalogItems.append(
                        CatalogItem(headers[headerIdx], catalogItemsRow[headerIdx])
                    )

        self._catalogItemDAO.truncate()
        self._catalogItemDAO.bulk_add(catalogItems)

        listsMD5Setting.text = cloudListsMD5
        self._settingsDAO.add_or_update(listsMD5Setting)

        self.emitter.catalogs_updated.emit()
