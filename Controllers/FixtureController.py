import os
from Core.Enums.FixtureMode import FixtureMode
from Core.Enums.FixtureStatus import FixtureStatus
from Core.Enums.SettingType import SettingType
from DataAccess.FctHostControlDAO import FctHostControlDAO
from DataAccess.FixtureDAO import FixtureDAO
from DataAccess.FixtureStatusLogDAO import FixtureStatusLogDAO
from DataAccess.CatalogItemDAO import CatalogItemDAO
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.MaintenanceDAO import MaintenanceDAO
from DataAccess.TestDAO import TestDAO
from datetime import datetime, timedelta
from Models.Fixture import Fixture
from Models.Maintenance import Maintenance
from Models.Test import Test


class FixtureController:
    def __init__(self) -> None:
        self._testDAO = TestDAO()
        self._fixtureDAO = FixtureDAO()
        self._mainConfigDAO = MainConfigDAO()
        self._fctHostControlDAO = FctHostControlDAO()
        self._maintenanceDAO = MaintenanceDAO()
        self._fixtureStatusLogDAO = FixtureStatusLogDAO()
        self._catalogItemDAO = CatalogItemDAO()

    def get_fct_host_cmd(self, fixture: Fixture, hasTraceability: bool):
        fullpathSplit = (
            self._fctHostControlDAO.get_fct_host_control_executable_fullpath().split(
                "/"
            )
        )
        fileName = fullpathSplit[-1]
        path = "/".join(fullpathSplit[0:-1])
        cmd = f"cd {path} && source ~/.bashrc && pyenv activate fctHostControl && python --version && which python && {self._mainConfigDAO.get_fixture_ip_env_name()}={fixture.ip} ./{fileName} -f {fixture.id}"
        if os.environ.get("ENV") == "testing":
            cmd = f"cd {path} && {self._mainConfigDAO.get_fixture_ip_env_name()}={fixture.ip} ./{fileName} -f {fixture.id}"
        if hasTraceability == False:
            cmd += " -m"
        return cmd

    def find(self, fixtureIp: str) -> Fixture:
        return self._fixtureDAO.find(fixtureIp)

    def find_last_tests(self, fixture: Fixture) -> Fixture:
        return self._fixtureDAO.find_last_tests(fixture)

    def add_test(self, fixture: Fixture, test: Test):
        if fixture.is_upload_to_sfc(test):
            isUploadOk = self._fixtureDAO.upload_pass_to_sfc(test.serialNumber)
            test.description += f" Xandra SFC Upload: {'OK' if isUploadOk else 'error'}"
        self._testDAO.add(test, fixture.mode.value)

    def add_status_log(
        self,
        fixture: Fixture,
        status: FixtureStatus,
        startDateTime: datetime,
        timeDelta: timedelta,
    ):
        self._fixtureStatusLogDAO.add(fixture, status, startDateTime, timeDelta)

    def add_maintenance(
        self,
        maintenance: Maintenance,
    ):
        self._maintenanceDAO.add(maintenance)

    def update_maintenance(
        self,
        maintenance: Maintenance,
    ):
        self._maintenanceDAO.update(maintenance)

    def update(self, fixture: Fixture):
        self._fixtureDAO.create_or_update(fixture)

    def calc_mode(self, hasTraceability: bool, isRetestMode: bool) -> FixtureMode:
        if not hasTraceability and isRetestMode:
            return FixtureMode.ONLY_REPORT_PASS
        if isRetestMode:
            return FixtureMode.RETEST
        if not hasTraceability:
            return FixtureMode.OFFLINE
        return FixtureMode.ONLINE

    def get_maintenance_parts(self):
        return self._catalogItemDAO.find_group_values(
            SettingType.SPARE_PARTS_LAST_SYNC.group
        )

    def get_maintenance_actions(self):
        return self._catalogItemDAO.find_group_values(
            SettingType.ACTIONS_LAST_SYNC.group
        )
