import math
import os
import json


class FixtureYieldChecker:
    BASE_PATH = "/usr/local/Foxconn/automation/Xandra/Resources"
    DISABLED_FIXTURES_JSON = f"{BASE_PATH}/disabled_fixtures.json"
    GREEN_COLOR = "\033[92m"
    RED_COLOR = "\033[91m"
    END_COLOR = "\033[0m"

    def __init__(self):
        self._result_file = f"{FixtureYieldChecker.BASE_PATH}/chk_station_yield.result"
        os.environ["RESULTFILE"] = self._result_file
        print(f"Result file path: {self._result_file}")
        if os.path.exists(self._result_file):
            os.remove(self._result_file)

    def check(self) -> bool:
        with open(FixtureYieldChecker.DISABLED_FIXTURES_JSON) as json_file:
            disabledFixtures = json.load(json_file)
            fixtureIp = os.getenv("XANDRA_FIXTURE_IP")
            if fixtureIp in disabledFixtures and disabledFixtures[fixtureIp] == True:
                self.outputFail()
                return False
            else:
                self.outputPass()
                return True

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


if FixtureYieldChecker().check() == False:
    exit(1)
else:
    exit(0)
