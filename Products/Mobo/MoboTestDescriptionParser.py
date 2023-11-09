import os
import subprocess
from Models.Test import Test
from Models.TestAnalysis import TestAnalysis
from Utils.ReverseReader import ReverseReader
import logging
import re


class MoboTestDescriptionParser:
    CHK_L6_INITIAL_STATUS_FILE = "chk_l6_initial_status.log"
    SECOND_LAYER_FAIL = "second_layer_fail.txt"

    def __init__(self) -> None:
        self._version = 1

    def parse(self, testAnalysis: TestAnalysis) -> str:
        try:
            description = ""
            secondLayerFail = self.second_layer_fail(testAnalysis)
            if secondLayerFail != "":
                description += f"Second Layer: {secondLayerFail}; "

            if testAnalysis.is_l6_initial_error():
                description += self.l6_initial_error(testAnalysis)

            return description
        except Exception as e:
            logging.error(str(e))
            return ""

    def second_layer_fail(self, testAnalysis: TestAnalysis) -> str:
        secondLayerFail = testAnalysis.get_out_log_path(self.SECOND_LAYER_FAIL)
        if not os.path.isfile(secondLayerFail):
            return ""
        try:
            return subprocess.getoutput(f"cat {secondLayerFail}")
        except Exception as e:
            return ""

    def l6_initial_error(self, testAnalysis: TestAnalysis) -> str:
        l6InitialFile = testAnalysis.get_out_log_path(self.CHK_L6_INITIAL_STATUS_FILE)
        if not os.path.isfile(l6InitialFile):
            return ""
        try:
            errors = subprocess.getoutput(
                f'grep -Poi ".+ERROR$" {l6InitialFile} | tr "\n" ","'
            )
            return self._remove_trailing_comma(errors)
        except Exception as e:
            return ""

    def _remove_trailing_comma(self, text: str) -> str:
        if text.endswith(","):
            return text[:-1]
        return text
