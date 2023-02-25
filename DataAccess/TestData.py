from automapper import mapper
from DataAccess.GoogleSheet import GoogleSheet
from DataAccess.MainConfigData import MainConfigData
from DataAccess.SqlAlchemyBase import Session
from Models.DTO.TestDTO import TestDTO
from Models.Test import Test


class TestData:

    def __init__(self) -> None:
        self._googleSheet = GoogleSheet()
        self._mainConfigData = MainConfigData()

    def add(self, test: Test, addToGoogleSheets: bool = True):
        if test.fixtureIp == None:
            return
        session = Session()
        session.add(mapper.to(TestDTO).map(test))
        session.commit()
        session.close()
        Session.remove()
        if addToGoogleSheets:
            self._googleSheet.add(test)

    def get_yield(self, fixtureIp: str) -> float:
        tests = self.find_last(fixtureIp)
        if len(tests) == 0:
            return 100
        passTests = 0
        for test in tests:
            if test.status:
                passTests += 1
        return round((passTests / len(tests)) * 100, 2)

    def are_last_test_pass(self, fixtureIp: str, qty: int = 3) -> bool:
        tests = self.find_last(fixtureIp, qty)
        if len(tests) > 0:
            for test in tests:
                if not test.status:
                    return False
        return True

    def find_last(
        self, fixtureIp: str, onlyFailures: bool = False
    ) -> "list[Test]":
        session = Session()
        query = (
            session.query(TestDTO)
            .filter(TestDTO.fixtureIp == fixtureIp)
            .order_by(TestDTO.endTime.desc(), TestDTO.id.desc())
        )
        if onlyFailures:
            query = query.filter(TestDTO.status == False)
        query = query.limit(self._mainConfigData.get_yield_calc_qty())
        tests: "list[Test]" = []
        for testDTO in query:
            tests.append(mapper.to(Test).map(testDTO))
        session.close()
        Session.remove()
        return tests

    def find_last_failures(self, fixtureIp: str) -> "list[Test]":
        return self.find_last(fixtureIp, onlyFailures=True)
