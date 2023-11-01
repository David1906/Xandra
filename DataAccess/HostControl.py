from abc import ABC, abstractmethod

from Models.Fixture import Fixture
from Models.FixtureConfig import FixtureConfig


class HostControl(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def get_start_cmd(self, fixture: Fixture, hasTraceability: bool) -> str:
        pass

    @abstractmethod
    def get_all_fixture_configs(self) -> "list[FixtureConfig]":
        pass

    @abstractmethod
    def get_upload_sfc_script_fullpath(self) -> str:
        pass

    @abstractmethod
    def get_script_fullpath(self) -> str:
        pass

    @abstractmethod
    def get_tool_fullpath(self) -> str:
        pass

    @abstractmethod
    def get_all_fixture_configs(self) -> "list[FixtureConfig]":
        pass

    @abstractmethod
    def get_script_version(self) -> str:
        pass

    @abstractmethod
    def get_automatic_product_selection(self) -> int:
        pass
