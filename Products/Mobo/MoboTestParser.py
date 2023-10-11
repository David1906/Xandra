from datetime import datetime
from DataAccess.TestParser import TestParser
from Models.Test import Test
from Products.C4.C4TestDescriptionParser import C4TestDescriptionParser
import logging
import re


class MoboTestParser(TestParser):
    REGEX_RESULT = "^result\s*:(pass|failed)+\s*"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(MoboTestParser, cls).__new__(cls, *args, **kwargs)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self) -> None:
        if self.initialized:
            return
        else:
            self.initialized = True

        self._testDescriptionParser = C4TestDescriptionParser()

    def parse(self, fullPath: str) -> Test:
        try:
            with open(fullPath, "r") as fp:
                test = Test()
                test.fullPath = fullPath
                for l_no, line in enumerate(fp):
                    if test.serialNumber == None and self.search("Board\s*SN", line):
                        test.serialNumber = self.extract_value(line)
                        continue

                    if test.project == None and self.search("Project\s*Name", line):
                        test.project = self.extract_value(line)
                        continue

                    if test.startTime == None and self.search("Start\s*Time", line):
                        test.startTime = self.extract_date_time(line)
                        continue

                    if test.endTime == None and self.search("End\s*Time", line):
                        test.endTime = self.extract_date_time(line)
                        continue

                    if test.codeVersion == None and self.search(
                        "test\s*code\s*ver", line
                    ):
                        test.codeVersion = self.extract_value(line)
                        continue

                    if test.fixtureIp == None and self.search("FixtureIP", line):
                        value = self.extract_value(line)
                        if value != "":
                            test.fixtureIp = value
                        continue

                    if test.status == None and self.search("result", line):
                        test.status = self.search("pass", line)
                        test.stepLabel = re.sub(
                            MoboTestParser.REGEX_RESULT, "", line, flags=re.I
                        ).strip()
                        continue

                    if test.operator == None and self.search("OperatorID", line):
                        test.operator = self.extract_value(line)
                        continue

                    if test.is_complete():
                        break

                test.description = self._testDescriptionParser.parse(test, fullPath)
                return test
        except Exception as e:
            logging.error(str(e))
            return Test()

    def search(self, pattern: str, string: str) -> bool:
        return re.search(pattern, string, re.IGNORECASE) != None

    def extract_date_time(self, line: str) -> datetime:
        value = self.extract_value(line)
        dt = datetime.strptime(value, "%Y%m%d_%H%M%S")
        return dt

    def extract_value(self, line: str) -> str:
        return line.split(":")[1].strip()
