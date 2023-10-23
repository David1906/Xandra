from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.TestAnalyzer import TestAnalyzer
from Products.C4.C4TestAnalyzer import C4TestAnalyzer
from Products.Mobo.MoboTestAnalyzer import MoboTestAnalyzer


class TestAnalyzerBuilder:
    def __init__(self) -> None:
        self._mainConfigDAO = MainConfigDAO()

    def build_based_on_main_config(
        self, fixtureId: str, sessionId: str
    ) -> TestAnalyzer:
        return self.build(self._mainConfigDAO.get_product(), fixtureId, sessionId)

    def build(self, model: str, fixtureId: str, sessionId: str) -> TestAnalyzer:
        if model == "C4":
            return C4TestAnalyzer(fixtureId, sessionId)
        elif model == "MOBO":
            return MoboTestAnalyzer(fixtureId, sessionId)
