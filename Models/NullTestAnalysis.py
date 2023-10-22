from Core.Enums.TestStatus import TestStatus
from Models.TestAnalysis import TestAnalysis


class NullTestAnalysis(TestAnalysis):
    def __init__(self) -> None:
        super().__init__(TestStatus.Initial, stepLabel="")
