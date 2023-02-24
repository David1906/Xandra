from automapper import mapper
from DataAccess.GoogleSheet import GoogleSheet
from DataAccess.SqlAlchemyBase import Session
from datetime import datetime
from Models.DTO.TestDTO import TestDTO
from Models.Test import Test
import logging, re

# TODO SEPARAR TEST PARSER

class TestData:
    REGEX_RESULT = "^result\s*:(pass|failed)+\s*"

    def __init__(self) -> None:
        self.googleSheet = GoogleSheet()

    def parse(self, fullPath: str) -> Test:
        try:
            with open(fullPath, "r") as fp:
                test = Test()
                for l_no, line in enumerate(fp):
                    if test.serialNumber == None and self.search("Board\s*SN", line):
                        test.serialNumber = self.extractValue(line)
                        continue

                    if test.project == None and self.search("Project\s*Name", line):
                        test.project = self.extractValue(line)
                        continue

                    if test.startTime == None and self.search("Start\s*Time", line):
                        test.startTime = self.extractDateTime(line)
                        continue

                    if test.endTime == None and self.search("End\s*Time", line):
                        test.endTime = self.extractDateTime(line)
                        continue

                    if test.codeVersion == None and self.search(
                        "test\s*code\s*ver", line
                    ):
                        test.codeVersion = self.extractValue(line)
                        continue

                    if test.fixtureIp == None and self.search("FixtureIP", line):
                        value = self.extractValue(line)
                        if value != "":
                            test.fixtureIp = value
                        continue

                    if test.status == None and self.search("result", line):
                        test.status = self.search("pass", line)
                        test.stepLabel = re.sub(
                            TestData.REGEX_RESULT, "", line, flags=re.I
                        ).strip()
                        continue

                    if test.operator == None and self.search("OperatorID", line):
                        test.operator = self.extractValue(line)
                        continue

                    if test.isComplete():
                        break
                return test
        except Exception as e:
            logging.error(str(e))
            return Test()

    def search(self, pattern: str, string: str) -> bool:
        return re.search(pattern, string, re.IGNORECASE) != None

    def extractDateTime(self, line: str) -> datetime:
        value = self.extractValue(line)
        dt = datetime.strptime(value, "%Y%m%d_%H%M%S")
        return dt

    def extractValue(self, line: str) -> str:
        return line.split(":")[1].strip()

    def add(self, test: Test, addToGoogleSheets: bool = True):
        if test.fixtureIp == None:
            return
        session = Session()
        session.add(mapper.to(TestDTO).map(test))
        session.commit()
        session.close()
        Session.remove()
        self.find(test.fixtureIp)
        self.findFailures(test.fixtureIp)
        if addToGoogleSheets:
            self.googleSheet.add(test)

    def getYield(self, fixtureIp: str, qty: int = 10) -> float:
        tests = self.find(fixtureIp, qty)
        if len(tests) == 0:
            return 100
        passTests = 0
        for test in tests:
            if test.status:
                passTests += 1
        return round((passTests / len(tests)) * 100, 2)

    def areLastTestPass(self, fixtureIp: str, qty: int = 3) -> bool:
        tests = self.find(fixtureIp, qty)
        if len(tests) > 0:
            for test in tests:
                if not test.status:
                    return False
        return True

    def find(
        self, fixtureIp: str, qty: int = 10, onlyFailures: bool = False
    ) -> "list[Test]":
        session = Session()
        query = (
            session.query(TestDTO)
            .filter(TestDTO.fixtureIp == fixtureIp)
            .order_by(TestDTO.id.desc())
        )
        if onlyFailures:
            query = query.filter(TestDTO.status == False)
        query = query.limit(qty)
        tests: "list[Test]" = []
        for testDTO in query:
            tests.append(mapper.to(Test).map(testDTO))
        session.close()
        Session.remove()
        return tests

    def findFailures(self, fixtureIp: str, qty: int = 10) -> "list[Test]":
        return self.find(fixtureIp, qty, onlyFailures=True)
