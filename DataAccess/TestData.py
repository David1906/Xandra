from Models.Fixture import Fixture
from automapper import mapper
from Core.Enums.FixtureMode import FixtureMode
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
        test.id = testDTO.id
        session.close()
        Session.remove()
        self._googleSheet.add(test)

    def find_last_by_fixture(self, fixture: Fixture):
        minQty = fixture.get_min_tests_qty()
        yieldQty = self._mainConfigData.get_yield_calc_qty()
        return self.find_last(
            fixture.ip,
            qty=yieldQty if yieldQty > minQty else minQty,
            ignoreRetest=fixture.mode != FixtureMode.RETEST,
        )

    def find_last(
        self,
        fixtureIp: str,
        qty: int = 0,
        onlyFailures: bool = False,
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

        if ignoreRetest:
            query = query.filter(TestDAO.mode != FixtureMode.RETEST.value)

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
