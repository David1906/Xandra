import subprocess
from DataAccess.DisabledFixturesData import DisabledFixturesData
from DataAccess.FixtureData import FixtureData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.YieldData import YieldData
from Models.Fixture import Fixture


class FixtureController:
    def __init__(self) -> None:
        self._fixtureData = FixtureData()
        self._mainConfigData = MainConfigData()

    def getLaunchFctHostCmd(self, fixture: Fixture, hasTraceability: bool):
        cmd = f"{self._mainConfigData.get_fixture_ip_env_name()}={fixture.ip} {self._mainConfigData.get_fct_host_control_fullpath()} -f {fixture.id}"
        if hasTraceability == False:
            cmd += " -m"
        return cmd

    def update(self, fixture: Fixture):
        self._fixtureData.createOrUpdate(fixture)

    def getLastTestPassQty(self):
        return self._mainConfigData.get_last_test_pass_qty()
