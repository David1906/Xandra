from Models.Fixture import Test
from PyQt5.QtCore import Qt
from Views.LastLogsWindow import LastLogsWindow


class LastTestsWindow(LastLogsWindow):
    def __init__(self, fixtureIp: str, showRetest: bool = False):
        super().__init__(
            fixtureIp, title=f"Last Tests - Fixture {fixtureIp}", showRetest=showRetest
        )

    def getTests(self, qty: int):
        return self._testDAO.find_last(
            self.fixtureIp, qty=qty, ignoreRetest=not self.is_show_retest()
        )

    def getResults(self, tests: "list[Test]"):
        results = {}
        for test in tests:
            key = "PASS" if test.status else "FAILED"
            if key == "":
                key = "unknown"
            if key in results:
                results[key] = results[key] + 1
            else:
                results[key] = 1
        return results

    def processSlice(self, slice):
        if slice.label() == "PASS":
            slice.setBrush(Qt.green)
        else:
            slice.setBrush(Qt.red)
