from Core.Enums.FixtureMode import FixtureMode
from DataAccess.FctHostControlDAO import FctHostControlDAO
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.SqlAlchemyBase import Session
from DataAccess.TestDAO import TestDAO
from Models.DTO.FixtureDTO import FixtureDTO
from Models.Fixture import Fixture
from sqlalchemy import update
from typing import Tuple
import subprocess


class FixtureDAO:
    def __init__(self) -> None:
        self._fctHostControlDAO = FctHostControlDAO()
        self._mainConfigDAO = MainConfigDAO()
        self._testDAO = TestDAO()

    def save(self, fixtures: "list[Fixture]"):
        for fixture in fixtures:
            self.create_or_update(fixture)

    def create_or_update(self, fixture: Fixture):
        session = Session()
        fixtureDTO = (
            session.query(FixtureDTO).where(FixtureDTO.ip == fixture.ip).first()
        )
        if fixtureDTO == None:
            fixtureDTO = FixtureDTO(
                ip=fixture.ip,
                mode=fixture.mode.value,
                abortTest=False,
                enableLock=fixture.isLockEnabled,
            )
            session.add(fixtureDTO)
        else:
            session.execute(
                update(FixtureDTO)
                .where(FixtureDTO.ip == fixture.ip)
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
        for fixture in session.query(FixtureDTO).all():
            fixture.mode = FixtureMode.ONLINE.value
        session.commit()
        Session.remove()

    def find_all(self) -> "list[Fixture]":
        fixtures = []
        for fixtureConfig in self._fctHostControlDAO.get_all_fixture_configs():
            fixtures.append(
                self.find(
                    fixtureConfig[FctHostControlDAO.PLC_IP_KEY],
                    fixtureConfig[FctHostControlDAO.PLC_ID_KEY],
                )
            )
        return fixtures

    def find(self, fixtureIp: str, id: str) -> Fixture:
        fixtureDTO = self.find_DTO_or_default(fixtureIp)
        fixture = Fixture(
            id=int(id),
            ip=fixtureIp,
            yieldErrorThreshold=self._mainConfigDAO.get_yield_error_threshold(),
            yieldWarningThreshold=self._mainConfigDAO.get_yield_warning_threshold(),
            lockFailQty=self._mainConfigDAO.get_lock_fail_qty(),
            unlockPassQty=self._mainConfigDAO.get_unlock_pass_qty(),
            mode=FixtureMode(fixtureDTO.mode),
        )
        fixture.tests = self.find_last_tests(fixture)
        return fixture

    def find_last_tests(self, fixture: Fixture) -> "list[Fixture]":
        return self._testDAO.find_last_by_fixture(fixture)

    def find_DTO_or_default(self, fixtureIp: str) -> FixtureDTO:
        fixtureDTO = self.find_DTO(fixtureIp)
        if fixtureDTO == None:
            fixtureDTO = FixtureDTO()
        return fixtureDTO

    def find_DTO(self, fixtureIp: str) -> FixtureDTO:
        session = Session()
        data = session.query(FixtureDTO).where(FixtureDTO.ip == fixtureIp).first()
        session.close()
        Session.remove()
        return data

    def should_abort_test(self, fixtureIp: str) -> bool:
        session = Session()
        data = session.query(FixtureDTO).where(FixtureDTO.ip == fixtureIp).first()
        session.close()
        Session.remove()
        if data == None:
            return False
        return data.abortTest

    def upload_pass_to_sfc(self, serialNumber) -> bool:
        result = subprocess.run(
            f'{self._fctHostControlDAO.get_upload_sfc_script_fullpath()} -s "{serialNumber}"',
            stdout=subprocess.PIPE,
            shell=True,
            cwd=self._fctHostControlDAO.get_script_fullpath(),
        )
        print(result.stdout.decode())
        return result.returncode == 0
