from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.TerminalAnalyzer import TerminalAnalyzer
from Products.C4.C4TerminalAnalyzer import C4TerminalAnalyzer


class TerminalAnalyzerBuilder:
    def __init__(self) -> None:
        self._mainConfigDAO = MainConfigDAO()

    def build_based_on_main_config(self, sessionId: str) -> TerminalAnalyzer:
        return self.build(self._mainConfigDAO.get_product(), sessionId)

    def build(self, model: str, sessionId: str) -> TerminalAnalyzer:
        if model == "C4":
            return C4TerminalAnalyzer(sessionId)
