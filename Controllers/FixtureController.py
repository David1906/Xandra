import subprocess
from DataAccess.DisabledFixturesData import DisabledFixturesData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.YieldData import YieldData
from Models.Fixture import Fixture


class FixtureController:
    def __init__(self) -> None:
        self._yieldData = YieldData()
        self._disabledFixturesData = DisabledFixturesData()

    def launch_fct_host_control(self, fixture: Fixture, hasTraceability: bool):
        mainConfigData = MainConfigData()
        cmd = f"{mainConfigData.get_fixture_ip_env_name()}={fixture.ip} {mainConfigData.get_fct_host_control_fullpath()} -f {fixture.id}"
        if hasTraceability == False:
            cmd += " -m"
        print(cmd)
        subprocess.call([mainConfigData.get_terminal(), "--", "bash", "-c", cmd])

    def update_yield_lock_skipped(self, fixture: Fixture):
        self._yieldData.update_yield_lock_skipped(fixture)
        self._disabledFixturesData.update(fixture)
