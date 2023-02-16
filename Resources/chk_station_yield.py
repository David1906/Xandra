import math
import os
import json


class FixtureYieldChecker:
    DISABLED_FIXTURES_JSON = "/home/david/Xandra/Resources/disabled_fixtures.json"
    GREEN_COLOR = "\033[92m"
    RED_COLOR = "\033[91m"
    END_COLOR = "\033[0m"

    def __init__(self):
        self._script_path = os.getenv("SCRIPTPATH")
        if self._script_path == None:
            self._script_path = "."
        self._result_file = f"{self._script_path}/station_yield.result"
        os.environ["RESULTFILE"] = self._result_file

        if os.path.exists(self._result_file):
            os.remove(self._result_file)

    def check(self):
        with open(FixtureYieldChecker.DISABLED_FIXTURES_JSON) as json_file:
            disabledFixtures = json.load(json_file)
            fixtureIp = os.getenv("XANDRA_FIXTURE_IP")
            if fixtureIp in disabledFixtures and disabledFixtures[fixtureIp] == True:
                self.outputFail()
            else:
                self.outputPass()

    def outputPass(self):
        self.printHeader(
            "Yield OK",
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


FixtureYieldChecker().check()
