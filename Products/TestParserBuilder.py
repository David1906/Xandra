from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.TestParser import TestParser
from Products.C4.C4TestParser import C4TestParser


class TestParserBuilder:
    def __init__(self) -> None:
        self._mainConfigDAO = MainConfigDAO()

    def build_based_on_main_config(self) -> TestParser:
        return self.build(self._mainConfigDAO.get_product())

    def build(self, model: str) -> TestParser:
        if model == "C4":
            return C4TestParser()
