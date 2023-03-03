from automapper import mapper
from DataAccess.GoogleSheet import GoogleSheet
from DataAccess.MainConfigData import MainConfigData
from DataAccess.SqlAlchemyBase import Session
from Models.DAO.TestDAO import TestDAO
from Models.Fixture import Test
from sqlalchemy import or_


class TestData:
    def __init__(self) -> None:
        self._googleSheet = GoogleSheet()
        self._mainConfigData = MainConfigData()

    def add(self, test: Test):
        if test.fixtureIp == None:
            return
        session = Session()
        session.add(mapper.to(TestDAO).map(test))
        session.commit()
        session.close()
        Session.remove()
        self._googleSheet.add(test)

    def get_yield(self, fixtureIp: str) -> float:
        tests = self.find_last(fixtureIp, ignoreOfflineFailures=True)
        if len(tests) == 0:
            return 100
        passTests = 0
        for test in tests:
            if test.status:
                passTests += 1
        return round((passTests / len(tests)) * 100, 2)

    def are_last_test_pass(self, fixtureIp: str, qty: int = 0) -> bool:
        configUnlockQty = self._mainConfigData.get_unlock_pass_qty()
        if configUnlockQty == 0:
            return True
        tests = self.find_last(fixtureIp, configUnlockQty if qty == 0 else qty)
        if len(tests) == 0:
            return False
        for test in tests:
            if not test.status:
                return False
        return True

    def find_last(
        self,
        fixtureIp: str,
        qty: int = 0,
        onlyFailures: bool = False,
        ignoreOfflineFailures: bool = False,
    ) -> "list[Test]":
        session = Session()
        query = (
            session.query(TestDAO)
            .filter(TestDAO.fixtureIp == fixtureIp)
            .order_by(TestDAO.endTime.desc(), TestDAO.id.desc())
        )

        if onlyFailures:
            query = query.filter(TestDAO.status == False)

        if ignoreOfflineFailures:
            query = query.filter(
                or_(TestDAO.countInYield == True, TestDAO.status == True)
            )

        query = query.limit(
            self._mainConfigData.get_yield_calc_qty() if qty == 0 else qty
        )
        tests: "list[Test]" = []
        for testDTO in query:
            tests.append(mapper.to(Test).map(testDTO))
        session.close()
        Session.remove()
        return tests

    def find_last_failures(self, fixtureIp: str, qty: int) -> "list[Test]":
        return self.find_last(fixtureIp, qty=qty, onlyFailures=True)
