from DataAccess.HostControl import HostControl
from DataAccess.MainConfigDAO import MainConfigDAO
from Models.Fixture import Fixture
from Models.FixtureConfig import FixtureConfig
from Products.C4.C4FctHostControlDAO import C4FctHostControlDAO
import os


class C4HostControl(HostControl):
    def __init__(self) -> None:
        super().__init__()
        self._fctHostControlDAO = C4FctHostControlDAO()
        self._mainConfigDAO = MainConfigDAO()

    def initialize(self):
        self._fctHostControlDAO.write_default_settings()

    def get_start_cmd(self, fixture: Fixture, hasTraceability: bool) -> str:
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

    def get_all_fixture_configs(self) -> "list[FixtureConfig]":
        fixtures: "list[FixtureConfig]" = []
        for fixtureConfig in self._fctHostControlDAO.get_all_fixture_configs():
            fixtures.append(
                FixtureConfig(
                    id=fixtureConfig[C4FctHostControlDAO.PLC_ID_KEY],
                    ip=fixtureConfig[C4FctHostControlDAO.PLC_IP_KEY],
                )
            )
        return fixtures

    def get_upload_sfc_script_fullpath(self) -> str:
        return self._fctHostControlDAO.get_upload_sfc_script_fullpath()

    def get_script_fullpath(self) -> str:
        return self._fctHostControlDAO.get_script_fullpath()

    def get_script_version(self) -> str:
        return "C4 - " + self._fctHostControlDAO.get_script_version()
