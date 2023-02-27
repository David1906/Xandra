#!/usr/bin/env python3
import math
import os
from SocketClient import SocketClient


class FixtureYieldChecker:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    GREEN_COLOR = "\033[92m"
    RED_COLOR = "\033[91m"
    END_COLOR = "\033[0m"

    def __init__(self):
        self._socketClient = SocketClient()
        self._result_file = f"{FixtureYieldChecker.BASE_PATH}/chk_station_yield.result"
        os.environ["RESULTFILE"] = self._result_file
        if os.path.exists(self._result_file):
            os.remove(self._result_file)

    def check(self) -> bool:
        try:
            fixtureIp = os.getenv("XANDRA_FIXTURE_IP")
            isDisabled = self._socketClient.get_is_disabled(fixtureIp)
            if isDisabled:
                self.outputFail()
                self._socketClient.notify_test_end(fixtureIp)
                return False
            else:
                self.outputPass()
                return True
        except:
            self.outputNoConnection()
            return False

    def outputNoConnection(self):
        self.printHeader(
            "Connection Error With Xandra",
            FixtureYieldChecker.RED_COLOR,
        )
        self.outputResultFile("FAIL")

    def outputPass(self):
        self.printHeader(
            "Fixture Enabled",
            FixtureYieldChecker.GREEN_COLOR,
        )
        self.outputResultFile("PASS")

    def outputFail(self):
        self.printHeader(
            "Fixture Disabled Due To Low Yield",
            FixtureYieldChecker.RED_COLOR,
        )
        self.outputResultFile("FAIL")

    def printHeader(self, text, color, length=65):
        HEADER_CHAR = "*"
        sideSize = math.ceil(((length - len(text)) / 2) - 1)
        fullText = HEADER_CHAR * sideSize + " " + text + " " + HEADER_CHAR * sideSize
        fullText = fullText.ljust(length, HEADER_CHAR)
        self.printInColor(
            HEADER_CHAR * len(fullText),
            color,
        )
        self.printInColor(
            fullText,
            color,
        )
        self.printInColor(
            HEADER_CHAR * len(fullText),
            color,
        )

    def printInColor(self, text, color):
        print(f"{color}{text}{FixtureYieldChecker.END_COLOR}")

    def outputResultFile(self, result):
        with open(self._result_file, "w") as outfile:
            outfile.write(result)


if FixtureYieldChecker().check():
    exit(0)
else:
    exit(1)
