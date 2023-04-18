from Core.Enums.FixtureMode import FixtureMode
from DataAccess.FctHostControlData import FctHostControlData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.SqlAlchemyBase import Session
from DataAccess.TestData import TestData
from Models.DAO.FixtureDAO import FixtureDAO
from Models.Fixture import Fixture
from sqlalchemy import update
from typing import Tuple
import subprocess


class FixtureData:
    def __init__(self) -> None:
        self._fctHostControlData = FctHostControlData()
        self._mainConfigData = MainConfigData()
        self._testData = TestData()

    def save(self, fixtures: "list[Fixture]"):
        for fixture in fixtures:
            self.create_or_update(fixture)

    def create_or_update(self, fixture: Fixture):
        session = Session()
        fixtureDAO = (
            session.query(FixtureDAO).where(FixtureDAO.ip == fixture.ip).first()
        )
        if fixtureDAO == None:
            fixtureDAO = FixtureDAO(
                ip=fixture.ip,
                mode=fixture.mode.value,
                abortTest=False,
                enableLock=fixture.isLockEnabled,
            )
            session.add(fixtureDAO)
        else:
            session.execute(
                update(FixtureDAO)
                .where(FixtureDAO.ip == fixture.ip)
                .values(
                    mode=fixture.mode.value,
                    abortTest=fixture.should_abort_test(),
                    enableLock=fixture.isLockEnabled,
                )
            )
        session.commit()
        Session.remove()

    def reset_mode(self):
        session = Session()
        for fixture in session.query(FixtureDAO).all():
            fixture.mode = FixtureMode.ONLINE.value
        session.commit()
        Session.remove()

    def find_all(self) -> "list[Fixture]":
        fixtures = []
        for fixtureConfig in self._fctHostControlData.get_all_fixture_configs():
            fixtures.append(
                self.find(
                    fixtureConfig[FctHostControlData.PLC_IP_KEY],
                    fixtureConfig[FctHostControlData.PLC_ID_KEY],
                )
            )
        return fixtures

    def find(self, fixtureIp: str, id: str) -> Fixture:
        fixtureDAO = self.find_DAO_or_default(fixtureIp)
        fixture = Fixture(
            id=int(id),
            ip=fixtureIp,
            yieldErrorThreshold=self._mainConfigData.get_yield_error_threshold(),
            yieldWarningThreshold=self._mainConfigData.get_yield_warning_threshold(),
            lockFailQty=self._mainConfigData.get_lock_fail_qty(),
            unlockPassQty=self._mainConfigData.get_unlock_pass_qty(),
            mode=FixtureMode(fixtureDAO.mode),
        )
        fixture.tests = self.find_last_tests(fixture)
        return fixture

    def find_last_tests(self, fixture: Fixture) -> "list[Fixture]":
        return self._testData.find_last_by_fixture(fixture)

    def find_DAO_or_default(self, fixtureIp: str) -> FixtureDAO:
        fixtureDAO = self.find_DAO(fixtureIp)
        if fixtureDAO == None:
            fixtureDAO = FixtureDAO()
        return fixtureDAO

    def find_DAO(self, fixtureIp: str) -> FixtureDAO:
        session = Session()
        data = session.query(FixtureDAO).where(FixtureDAO.ip == fixtureIp).first()
        session.close()
        Session.remove()
        return data

    def should_abort_test(self, fixtureIp: str) -> bool:
        session = Session()
        data = session.query(FixtureDAO).where(FixtureDAO.ip == fixtureIp).first()
        session.close()
        Session.remove()
        if data == None:
            return False
        return data.abortTest

    def upload_pass_to_sfc(self, serialNumber) -> bool:
        result = subprocess.run(
            f'{self._fctHostControlData.get_upload_sfc_script_fullpath()} -s "{serialNumber}"',
            stdout=subprocess.PIPE,
            shell=True,
            cwd=self._fctHostControlData.get_script_fullpath(),
        )
        print(result.stdout.decode())
        return result.returncode == 0
