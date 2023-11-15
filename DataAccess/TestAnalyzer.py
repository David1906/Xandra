from abc import ABC, abstractmethod
from Core.Enums.TestStatus import TestStatus
from datetime import datetime
from Models.NullTestAnalysis import NullTestAnalysis
from Models.TestAnalysis import TestAnalysis


class TestAnalyzer(ABC):
    ERROR_ID = -1
    DELETE_NEW_LINE_PIPE = "| tr --delete '\n'"

    def __init__(self, sessionId: str) -> None:
        self.sessionId = sessionId
        self.prevLastLine = ""
        self.currentAnalysis = NullTestAnalysis()

    @abstractmethod
    def can_recover(self) -> bool:
        pass

    @abstractmethod
    def is_board_loaded(self) -> bool:
        pass

    @abstractmethod
    def initialize_files(self):
        pass

    @abstractmethod
    def refresh_board_data(self):
        pass

    @abstractmethod
    def is_testing(self) -> bool:
        pass

    @abstractmethod
    def is_finished(self) -> bool:
        pass

    @abstractmethod
    def is_board_released(self) -> bool:
        pass

    @abstractmethod
    def is_pass(self) -> bool:
        pass

    @abstractmethod
    def is_failed(self) -> bool:
        pass

    @abstractmethod
    def get_test_analysis(
        self, testStatus: TestStatus, stepLabel: str = None
    ) -> TestAnalysis:
        pass

    @abstractmethod
    def get_fixture_ip(self) -> str:
        pass
