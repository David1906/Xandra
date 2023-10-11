import math
import os
import requests


class HttpClient:
    SERVER_URL_FIXTURE_STATUS = (
        "http://127.0.0.1:5002/fixture/status?fixtureIp={fixtureIp}"
    )
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    RED_COLOR = "\033[91m"
    GREEN_COLOR = "\033[92m"
    WHITE_COLOR = "\033[97m"
    END_COLOR = "\033[0m"

    def __init__(self, resultFileName: str = "result.result"):
        self._result_file = f"{HttpClient.BASE_PATH}/{resultFileName}"
        os.environ["RESULTFILE"] = self._result_file
        if os.path.exists(self._result_file):
            os.remove(self._result_file)

    def is_locked(self, fixtureIp: str) -> bool:
        try:
            print(
                HttpClient.SERVER_URL_FIXTURE_STATUS.format(fixtureIp=fixtureIp),
                fixtureIp,
            )
            response = requests.get(
                HttpClient.SERVER_URL_FIXTURE_STATUS.format(fixtureIp=fixtureIp)
            )
            if response.json()["shouldAbortTest"]:
                self.outputFail("Fixture Locked")
                return False
            else:
                self.outputOk("Fixture Unlocked")
                return True
        except:
            self.outputNoConnection()
            return True

    def outputNoConnection(self):
        self.printHeader(
            "Connection Error With Xandra",
            HttpClient.WHITE_COLOR,
        )
        self.outputResultFile("PASS")

    def outputOk(self, text: str):
        self.printHeader(
            text,
            HttpClient.GREEN_COLOR,
        )
        self.outputResultFile("PASS")

    def outputFail(self, text: str):
        self.printHeader(
            text,
            HttpClient.RED_COLOR,
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
        print(f"{color}{text}{HttpClient.END_COLOR}")

    def outputResultFile(self, result):
        with open(self._result_file, "w") as outfile:
            outfile.write(result)
