from DataAccess.FixtureConfigData import FixtureConfigData
from DataAccess.FixtureData import FixtureData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.TestData import TestData
from Models.Fixture import Fixture


class FixtureController:
    def __init__(self) -> None:
        self._testData = TestData()
        self._fixtureData = FixtureData()
        self._fixtureConfigData = FixtureConfigData()
        self._mainConfigData = MainConfigData()

    def get_fct_host_cmd(self, fixture: Fixture, hasTraceability: bool):
        cmd = f"{self._mainConfigData.get_fixture_ip_env_name()}={fixture.get_ip()} {self._mainConfigData.get_fct_host_control_fullpath()} -f {fixture.get_id()}"
        if hasTraceability == False:
            cmd += " -m"
        return cmd

    def refresh(self, fixture: Fixture):
        fixture.set_config(self._fixtureConfigData.find(fixture.get_ip()))

    def find(self, fixtureIp: str) -> Fixture:
        return self._fixtureData.find(fixtureIp)

    def add_test(self, fixture: Fixture):
        self._testData.add(
            fixture._test, fixture.is_affecting_yield(), fixture.is_upload_to_sfc()
        )
        if fixture.is_upload_to_sfc():
            isUploadOk = self._fixtureData.upload_pass_to_sfc(
                fixture._test.serialNumber
            )
            fixture.hasErrorUploadingToSfc = not isUploadOk

    def update(self, fixture: Fixture):
        self._fixtureData.create_or_update(fixture)

    def get_last_test_pass_qty(self):
        return self._mainConfigData.get_unlock_pass_qty()
