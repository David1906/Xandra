import subprocess
from automapper import mapper
from DataAccess.FctHostControlData import FctHostControlData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.SqlAlchemyBase import Session
from DataAccess.TestData import TestData
from Models.DAO.FixtureDAO import FixtureDAO
from Models.Fixture import Fixture
from sqlalchemy import update
from subprocess import check_output


class FixtureData:
    def __init__(self) -> None:
        self._fctHostControlData = FctHostControlData()
        self._testData = TestData()
        self._mainConfigData = MainConfigData()

    def save(self, fixtures: "list[Fixture]"):
        for fixture in fixtures:
            self.create_or_update(fixture)

    def create_or_update(self, fixture: Fixture):
        session = Session()
        fixtureDAO = (
            session.query(FixtureDAO).where(FixtureDAO.ip == fixture.ip).first()
        )
        if fixtureDAO == None:
            fixtureDAO = mapper.to(FixtureDAO).map(fixture)
            fixtureDAO.isDisabled = (fixture.is_disabled(),)
            session.add(fixtureDAO)
        else:
            session.execute(
                update(FixtureDAO)
                .where(FixtureDAO.ip == fixture.ip)
                .values(
                    ip=fixture.ip,
                    isDisabled=fixture.is_disabled(),
                    isSkipped=fixture.isSkipped,
                    isRetestMode=fixture.isRetestMode,
                )
            )
        session.commit()
        Session.remove()

    def is_skipped(self, fixtureIp: str) -> bool:
        fixtureDAO = self.find_DTO(fixtureIp)
        if fixtureDAO == None:
            return False
        else:
            return fixtureDAO.isSkipped

    def is_retest_mode(self, fixtureIp: str) -> bool:
        fixtureDAO = self.find_DTO(fixtureIp)
        if fixtureDAO == None:
            return False
        else:
            return fixtureDAO.isRetestMode

    def find_DTO(self, fixtureIp: str) -> FixtureDAO:
        session = Session()
        data = session.query(FixtureDAO).where(FixtureDAO.ip == fixtureIp).first()
        session.close()
        Session.remove()
        return data

    def refresh(self, resetFixture: bool = False):
        for fixture in self.find_all():
            if resetFixture:
                fixture.reset()
            self.create_or_update(fixture)

    def find_all(self) -> "list[Fixture]":
        fixtures = []
        for fixture in self._fctHostControlData.get_all_fixture_configs():
            fixtures.append(self.find(fixture[FctHostControlData.PLC_IP_KEY]))
        return fixtures

    def find(self, fixtureIp: str) -> Fixture:
        for fixture in self._fctHostControlData.get_all_fixture_configs():
            if fixtureIp == fixture[FctHostControlData.PLC_IP_KEY]:
                return Fixture(
                    fixture[FctHostControlData.PLC_ID_KEY],
                    fixtureIp,
                    self._testData.get_yield(fixtureIp),
                    self._testData.are_last_test_pass(fixtureIp),
                    self.is_skipped(fixtureIp),
                    self._mainConfigData.get_yield_error_threshold(),
                    self._mainConfigData.get_yield_warning_threshold(),
                    isRetestMode=self.is_retest_mode(fixtureIp),
                )

    def upload_pass_to_sfc(self, serialNumber) -> bool:
        result = subprocess.run(
            [self._fctHostControlData.get_upload_sfc_script_fullpath()],
            stdout=subprocess.PIPE,
            shell=True,
            cwd=self._fctHostControlData.get_script_fullpath(),
        )
        print(result.stdout.decode())
        return result.returncode == 0
