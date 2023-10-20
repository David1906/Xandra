from DataAccess.HostControl import HostControl
from DataAccess.MainConfigDAO import MainConfigDAO
from Models.Fixture import Fixture
from Models.FixtureConfig import FixtureConfig
from Products.Mobo.MoboFctHostControlDAO import MoboFctHostControlDAO
import os



class MoboHostControl(HostControl):
    def __init__(self) -> None:
        super().__init__()
        self._fctHostControlDAO = MoboFctHostControlDAO()
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
            cmd = f"cd {path} && {self._mainConfigDAO.get_fixture_ip_env_name()}={fixture.ip} exec ./{fileName} -f {fixture.id}"
        if hasTraceability == False:
            cmd += " -m"
        return cmd

    def get_all_fixture_configs(self) -> "list[FixtureConfig]":
        fixtures: "list[FixtureConfig]" = []
        for fixtureConfig in self._fctHostControlDAO.get_all_fixture_configs():
            fixtures.append(
                FixtureConfig(
                    id=fixtureConfig[MoboFctHostControlDAO.PLC_ID_KEY],
                    ip=fixtureConfig[MoboFctHostControlDAO.PLC_IP_KEY],
                )
            )
        return fixtures[:9]

    def get_upload_sfc_script_fullpath(self) -> str:
        return self._fctHostControlDAO.get_upload_sfc_script_fullpath()

    def get_script_fullpath(self) -> str:
        return self._fctHostControlDAO.get_script_fullpath()

    def get_script_version(self) -> str:
        return "MOBO - " + self._fctHostControlDAO.get_script_version()

    def get_automatic_product_selection(self) -> int:
        return self._fctHostControlDAO.AUTOMATIC_PRODUCT_SELECTION
