#!/usr/bin/env python3
import math
import os
from SocketClient import SocketClient


class TestEndNotifier:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    RED_COLOR = "\033[91m"
    GREEN_COLOR = "\033[92m"
    WHITE_COLOR = "\033[97m"
    END_COLOR = "\033[0m"

    def __init__(self):
        self._socketClient = SocketClient()

    def notify(self) -> bool:
        try:
            fixtureIp = os.getenv("XANDRA_FIXTURE_IP")
            self._socketClient.notify_test_end(fixtureIp)
            self.printHeader("Test Finished", TestEndNotifier.WHITE_COLOR)
        except:
            pass

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
        print(f"{color}{text}{TestEndNotifier.END_COLOR}")

    def outputResultFile(self, result):
        with open(self._result_file, "w") as outfile:
            outfile.write(result)


TestEndNotifier().notify()
exit(0)
