from DataAccess.FctHostControlData import FctHostControlData
from DataAccess.FixtureConfigData import FixtureConfigData
from DataAccess.MainConfigData import MainConfigData
from Models.Fixture import Fixture
import subprocess


class FixtureData:
    def __init__(self) -> None:
        self._fctHostControlData = FctHostControlData()
        self._fixtureConfigData = FixtureConfigData()
        self._mainConfigData = MainConfigData()

    def save(self, fixtures: "list[Fixture]"):
        for fixture in fixtures:
            self._fixtureConfigData.create_or_update(fixture.get_config())

    def create_or_update(self, fixture: Fixture):
        self._fixtureConfigData.create_or_update(fixture.get_config())

    def is_skipped(self, fixtureIp: str) -> bool:
        return self._fixtureConfigData.is_skipped(fixtureIp)

    def is_retest_mode(self, fixtureIp: str) -> bool:
        return self._fixtureConfigData.is_retest_mode(fixtureIp)

    def refresh(self, resetFixture: bool = False):
        for fixture in self.find_all():
            if resetFixture:
                fixture.reset()
            self._fixtureConfigData.create_or_update(fixture.get_config())

    def find_all(self) -> "list[Fixture]":
        fixtures = []
        for fixture in self._fctHostControlData.get_all_fixture_configs():
            fixtures.append(self.find(fixture[FctHostControlData.PLC_IP_KEY]))
        return fixtures

    def find(self, fixtureIp: str) -> Fixture:
        fixtureConfig = self._fixtureConfigData.find(fixtureIp)
        return Fixture(fixtureConfig)

    def upload_pass_to_sfc(self, serialNumber) -> bool:
        result = subprocess.run(
            [
                self._fctHostControlData.get_upload_sfc_script_fullpath(),
                "-s",
                serialNumber,
            ],
            stdout=subprocess.PIPE,
            shell=True,
            cwd=self._fctHostControlData.get_script_fullpath(),
        )
        print(result.stdout.decode())
        return result.returncode == 0
