import os
import subprocess
from Models.Test import Test
from Models.TestAnalysis import TestAnalysis
from Utils.ReverseReader import ReverseReader
import logging
import re


class MoboTestDescriptionParser:
    CHK_L6_INITIAL_STATUS_FILE = "chk_l6_initial_status.log"

    def __init__(self) -> None:
        self._version = 1

    def parse(self, testAnalysis: TestAnalysis) -> str:
        try:
            if testAnalysis.is_l6_initial_error():
                return self.l6_initial_error(testAnalysis)
            else:
                return ""
        except Exception as e:
            logging.error(str(e))
            return ""

    def l6_initial_error(self, testAnalysis: TestAnalysis) -> str:
        if not os.path.isfile(testAnalysis.get_out_log_path()):
            return ""
        popen = subprocess.Popen(
            f'grep -Poi ".+ERROR$" {testAnalysis.get_out_log_path()}/{self.CHK_L6_INITIAL_STATUS_FILE} | tr "\n" ","',
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        popen.communicate()
        return (
            self._remove_trailing_comma(popen.stdout) if popen.returncode == 0 else ""
        )

    def _remove_trailing_comma(self, text: str) -> str:
        if text.endswith(","):
            return text[:-1]
        return text
