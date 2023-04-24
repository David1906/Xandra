from Models.Fixture import Fixture
from automapper import mapper
from Core.Enums.FixtureMode import FixtureMode
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.SqlAlchemyBase import Session
from Models.DTO.TestDTO import TestDTO
from Models.Fixture import Test


class TestDAO:
    def __init__(self) -> None:
        self._mainConfigDAO = MainConfigDAO()

    def add(self, test: Test, mode: int):
        if test.fixtureIp == None:
            return
        session = Session()
        try:
            testDTO = mapper.to(TestDTO).map(test)
            testDTO.mode = mode
            session.add(testDTO)
            session.commit()
            test.id = testDTO.id
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def find_last_by_fixture(self, fixture: Fixture):
        minQty = fixture.get_min_tests_qty()
        yieldQty = self._mainConfigDAO.get_yield_calc_qty()
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
            session.query(TestDTO)
            .filter(TestDTO.fixtureIp == fixtureIp)
            .order_by(TestDTO.endTime.desc(), TestDTO.id.desc())
        )

        if onlyFailures:
            query = query.filter(TestDTO.status == False)

        if ignoreRetest:
            query = query.filter(TestDTO.mode != FixtureMode.RETEST.value)

        query = query.limit(
            self._mainConfigDAO.get_yield_calc_qty() if qty == 0 else qty
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

    def find_not_sync(self) -> "list[Test]":
        session = Session()
        query = (
            session.query(TestDTO)
            .filter(TestDTO.isSync == False)
            .order_by(TestDTO.id.asc())
        )
        tests: "list[Test]" = []
        for testDTO in query:
            tests.append(mapper.to(Test).map(testDTO))
        session.close()
        Session.remove()
        return tests

    def update_is_sync(self, test: Test, isSync: bool):
        session = Session()
        try:
            (
                session.query(TestDTO)
                .filter(TestDTO.id == test.id)
                .update({"isSync": isSync})
            )
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()
