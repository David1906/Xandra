from Models.Fixture import Test
from PyQt5.QtCore import Qt
from Views.LastLogsWindow import LastLogsWindow


class LastFailuresWindow(LastLogsWindow):
    def __init__(self, fixtureIp: str):
        super().__init__(
            fixtureIp,
            title=f"Last Failures - Fixture {fixtureIp}",
            biggestSliceColor=Qt.red,
        )

    def getTests(self, qty: int):
        return self._testData.find_last_failures(
            self.fixtureIp, qty, onlyCountInYield=self.is_only_count_in_yield()
        )

    def getResults(self, tests: "list[Test]"):
        results = {}
        for test in tests:
            key = test.stepLabel
            if key == "":
                key = "unknown"
            if key in results:
                results[key] = results[key] + 1
            else:
                results[key] = 1
        return results
