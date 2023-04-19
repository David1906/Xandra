from Core.Enums.FixtureMode import FixtureMode
from Core.Enums.FixtureStatus import FixtureStatus
from DataAccess.FctHostControlData import FctHostControlData
from DataAccess.FixtureData import FixtureData
from DataAccess.FixtureStatusLogData import FixtureStatusLogData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.TestData import TestData
from datetime import datetime, timedelta
from Models.Fixture import Fixture
from Models.Test import Test


class FixtureController:
    def __init__(self) -> None:
        self._testData = TestData()
        self._fixtureData = FixtureData()
        self._mainConfigData = MainConfigData()
        self._fctHostControlData = FctHostControlData()
        self._fixtureStatusLogData = FixtureStatusLogData()

    def get_fct_host_cmd(self, fixture: Fixture, hasTraceability: bool):
        fullpathSplit = (
            self._fctHostControlData.get_fct_host_control_executable_fullpath().split(
                "/"
            )
        )
        fileName = fullpathSplit[-1]
        path = "/".join(fullpathSplit[0:-1])
        cmd = f"cd {path} && source ~/.bashrc && pyenv activate fctHostControl && python --version && which python && {self._mainConfigData.get_fixture_ip_env_name()}={fixture.ip} ./{fileName} -f {fixture.id}"
        if hasTraceability == False:
            cmd += " -m"
        return cmd

    def find(self, fixtureIp: str) -> Fixture:
        return self._fixtureData.find(fixtureIp)

    def find_last_tests(self, fixture: Fixture) -> Fixture:
        return self._fixtureData.find_last_tests(fixture)

    def add_test(self, fixture: Fixture, test: Test):
        if fixture.is_upload_to_sfc(test):
            isUploadOk = self._fixtureData.upload_pass_to_sfc(test.serialNumber)
            test.description += f" Xandra SFC Upload: {'OK' if isUploadOk else 'error'}"
        self._testData.add(test, fixture.mode.value)

    def add_status_log(
        self,
        fixture: Fixture,
        status: FixtureStatus,
        startDateTime: datetime,
        timeDelta: timedelta,
    ):
        self._fixtureStatusLogData.add(fixture, status, startDateTime, timeDelta)

    def update(self, fixture: Fixture):
        self._fixtureData.create_or_update(fixture)

    def calc_mode(self, hasTraceability: bool, isRetestMode: bool) -> FixtureMode:
        if not hasTraceability and isRetestMode:
            return FixtureMode.ONLY_REPORT_PASS
        if isRetestMode:
            return FixtureMode.RETEST
        if not hasTraceability:
            return FixtureMode.OFFLINE
        return FixtureMode.ONLINE
