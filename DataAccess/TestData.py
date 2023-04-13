from automapper import mapper
from Core.Enums.TestMode import TestMode
from DataAccess.GoogleSheet import GoogleSheet
from DataAccess.MainConfigData import MainConfigData
from DataAccess.SqlAlchemyBase import Session
from Models.DAO.TestDAO import TestDAO
from Models.Fixture import Test


class TestData:
    def __init__(self) -> None:
        self._googleSheet = GoogleSheet()
        self._mainConfigData = MainConfigData()

    def add(self, test: Test, mode: int):
        if test.fixtureIp == None:
            return
        testDTO = mapper.to(TestDAO).map(test)
        testDTO.mode = mode
        session = Session()
        session.add(testDTO)
        session.commit()
        session.close()
        Session.remove()
        self._googleSheet.add(test)

    def get_yield(self, fixtureIp: str, ignoreRetest: bool = False) -> float:
        tests = self.find_last(fixtureIp, ignoreRetest=ignoreRetest)
        if len(tests) == 0:
            return 100
        passTests = 0
        for test in tests:
            if test.status:
                passTests += 1
        return round((passTests / len(tests)) * 100, 2)

    def are_last_test_pass(self, fixtureIp: str) -> bool:
        return self.get_remaining_to_unlock(fixtureIp) <= 0

    def get_remaining_to_unlock(self, fixtureIp: str) -> bool:
        configUnlockQty = self._mainConfigData.get_unlock_pass_qty()
        configLockQty = self._mainConfigData.get_lock_fail_qty()
        tests = self.find_last(
            fixtureIp, configUnlockQty + configLockQty - 1, ignoreRetest=True
        )
        totalPass = 0
        for test in tests:
            if test.status:
                totalPass = totalPass + 1
        total = configUnlockQty - totalPass
        if len(tests) == 0 or total <= 0:
            return 0
        if tests[0].status == False:
            return configUnlockQty
        return total

    def are_last_test_fail(self, fixtureIp: str) -> bool:
        if self.are_last_test_pass(fixtureIp):
            return True

        configLockQty = self._mainConfigData.get_lock_fail_qty()
        if configLockQty == 0:
            return False
        tests = self.find_last(
            fixtureIp, configLockQty, ignoreOffline=True, ignoreRetest=True
        )
        if len(tests) == 0 or len(tests) < configLockQty:
            return False
        for test in tests:
            if test.status:
                return False
        return True

    def find_last(
        self,
        fixtureIp: str,
        qty: int = 0,
        onlyFailures: bool = False,
        ignoreOffline: bool = False,
        ignoreRetest: bool = False,
    ) -> "list[Test]":
        session = Session()
        query = (
            session.query(TestDAO)
            .filter(TestDAO.fixtureIp == fixtureIp)
            .order_by(TestDAO.endTime.desc(), TestDAO.id.desc())
        )

        if onlyFailures:
            query = query.filter(TestDAO.status == False)

        if ignoreOffline:
            query = query.filter(TestDAO.mode != TestMode.OFFLINE.value)

        if ignoreRetest:
            query = query.filter(TestDAO.mode != TestMode.RETEST.value)

        query = query.limit(
            self._mainConfigData.get_yield_calc_qty() if qty == 0 else qty
        )
        tests: "list[Test]" = []
        for testDTO in query:
            tests.append(mapper.to(Test).map(testDTO))
        session.close()
        Session.remove()
        return tests

    def find_last_failures(
        self,
        fixtureIp: str,
        qty: int,
        ignoreRetest: bool = False,
    ) -> "list[Test]":
        return self.find_last(
            fixtureIp, qty=qty, onlyFailures=True, ignoreRetest=ignoreRetest
        )
