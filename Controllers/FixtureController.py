from Core.Enums.FixtureMode import FixtureMode
from Core.Enums.FixtureStatus import FixtureStatus
from Core.Enums.SettingType import SettingType
from DataAccess.CatalogItemDAO import CatalogItemDAO
from DataAccess.FixtureDAO import FixtureDAO
from DataAccess.FixtureStatusLogDAO import FixtureStatusLogDAO
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.MaintenanceDAO import MaintenanceDAO
from DataAccess.TestDAO import TestDAO
from datetime import datetime, timedelta
from Models.Fixture import Fixture
from Models.Maintenance import Maintenance
from Models.TestAnalysis import TestAnalysis
from Models.Test import Test
from Products.HostControlBuilder import HostControlBuilder
from Products.TestParserBuilder import TestParserBuilder
import logging
import os
import pathlib


class FixtureController:
    def __init__(self) -> None:
        self._testDAO = TestDAO()
        self._fixtureDAO = FixtureDAO()
        self._mainConfigDAO = MainConfigDAO()
        self._hostControl = HostControlBuilder().build_based_on_main_config()
        self._maintenanceDAO = MaintenanceDAO()
        self._fixtureStatusLogDAO = FixtureStatusLogDAO()
        self._catalogItemDAO = CatalogItemDAO()
        self._testParser = TestParserBuilder().build_based_on_main_config()

    def get_fct_host_cmd(self, fixture: Fixture, hasTraceability: bool):
        return self._hostControl.get_start_cmd(fixture, hasTraceability)

    def find(self, fixtureIp: str) -> Fixture:
        return self._fixtureDAO.find(fixtureIp)

    def find_last_tests(self, fixture: Fixture) -> Fixture:
        return self._fixtureDAO.find_last_tests(fixture)

    def add_test(self, fixture: Fixture, test: Test):
        if fixture.is_upload_to_sfc(test):
            isUploadOk = self._fixtureDAO.upload_pass_to_sfc(test.serialNumber)
            test.description += f" Xandra SFC Upload: {'OK' if isUploadOk else 'error'}"
        test.fixtureIp = fixture.ip
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

    def parse_test(self, testAnalysis: TestAnalysis) -> Test:
        try:
            return self._testParser.parse(testAnalysis)
        except Exception as e:
            logging.error(str(e))

    def get_automatic_product_selection(self) -> int:
        return self._mainConfigDAO.get_automatic_product_selection()

    def get_fct_host_control_tool_path(self) -> int:
        return self._hostControl.get_tool_fullpath()

    def get_automatic_unlock(self) -> int:
        return self._mainConfigDAO.get_automatic_unlock()
