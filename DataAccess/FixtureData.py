from automapper import mapper
from DataAccess.FctHostControlData import FctHostControlData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.SqlAlchemyBase import Session
from DataAccess.TestData import TestData
from Models.DTO.FixtureDTO import FixtureDTO
from Models.Fixture import Fixture
from sqlalchemy import update


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
        fixtureDTO = (
            session.query(FixtureDTO).where(
                FixtureDTO.ip == fixture.ip).first()
        )
        if fixtureDTO == None:
            fixtureDTO = FixtureDTO(
                ip=fixture.ip, isDisabled=fixture.is_disabled(), isSkipped=fixture.isSkipped)
            session.add(fixtureDTO)
        else:
            session.execute(
                update(FixtureDTO)
                .where(FixtureDTO.ip == fixture.ip)
                .values(
                    ip=fixture.ip,
                    isDisabled=fixture.is_disabled(),
                    isSkipped=fixture.isSkipped,
                )
            )
        session.commit()
        Session.remove()

    def is_skipped(self, fixtureIp: str) -> bool:
        fixtureDTO = self.find_DTO(fixtureIp)
        if fixtureDTO == None:
            return False
        else:
            return fixtureDTO.isSkipped

    def find_DTO(self, fixtureIp: str) -> FixtureDTO:
        session = Session()
        data = session.query(FixtureDTO).where(
            FixtureDTO.ip == fixtureIp).first()
        session.close()
        Session.remove()
        return data

    def refresh(self):
        for fixture in self.find_all():
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
                )
