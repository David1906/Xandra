from SocketClient import SocketClient
import math
import os


class FixtureSocketNotifier:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    RED_COLOR = "\033[91m"
    GREEN_COLOR = "\033[92m"
    WHITE_COLOR = "\033[97m"
    END_COLOR = "\033[0m"

    def __init__(self, resultFileName: str = "result.result"):
        self._socketClient = SocketClient()
        self._result_file = f"{FixtureSocketNotifier.BASE_PATH}/{resultFileName}"
        os.environ["RESULTFILE"] = self._result_file
        if os.path.exists(self._result_file):
            os.remove(self._result_file)

    def is_locked(self, fixtureIp: str) -> bool:
        try:
            if self._socketClient.get_is_disabled(fixtureIp):
                self.outputFail("Fixture Locked")
                return False
            else:
                self.outputOk("Fixture Unlocked")
                return True
        except:
            self.outputNoConnection()
            return True

    def notify_test_start(self, fixtureIp: str) -> bool:
        try:
            self._socketClient.notify_test_start(fixtureIp)
            self.printHeader("Test Started", FixtureSocketNotifier.WHITE_COLOR)
        except:
            self.outputNoConnection()

    def notify_finish(
        self,
        fixtureIp: str,
        serialNumber: str = "",
        logFileName: str = "",
        currentTest: str = "",
    ) -> bool:
        try:
            self._socketClient.notify_test_end(fixtureIp, serialNumber, logFileName, currentTest)
            self.printHeader("Test Finished", FixtureSocketNotifier.WHITE_COLOR)
        except:
            self.outputNoConnection()

    def outputNoConnection(self):
        self.printHeader(
            "Connection Error With Xandra",
            FixtureSocketNotifier.WHITE_COLOR,
        )
        self.outputResultFile("PASS")

    def outputOk(self, text: str):
        self.printHeader(
            text,
            FixtureSocketNotifier.GREEN_COLOR,
        )
        self.outputResultFile("PASS")

    def outputFail(self, text: str):
        self.printHeader(
            text,
            FixtureSocketNotifier.RED_COLOR,
        )
        self.outputResultFile("FAIL")

    def printHeader(self, text, color, length=65):
        HEADER_CHAR = "*"
        halfTextLen = math.ceil(((length - len(text)) / 2) - 1)
        fullText = (
            HEADER_CHAR * halfTextLen + " " + text + " " + HEADER_CHAR * halfTextLen
        )
        fullText = fullText.ljust(length, HEADER_CHAR)
        self.printColored(
            HEADER_CHAR * len(fullText),
            color,
        )
        self.printColored(
            fullText,
            color,
        )
        self.printColored(
            HEADER_CHAR * len(fullText),
            color,
        )

    def printColored(self, text, color):
        print(f"{color}{text}{FixtureSocketNotifier.END_COLOR}")

    def outputResultFile(self, result):
        with open(self._result_file, "w") as outfile:
            outfile.write(result)
