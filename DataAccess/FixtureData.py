from automapper import mapper
from sqlalchemy import update
from DataAccess.FctHostControlData import FctHostControlData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.SqlAlchemyBase import Session
from DataAccess.TestData import TestData
from Models.DTO.FixtureDTO import FixtureDTO
from Models.Fixture import Fixture


class FixtureData:
    def __init__(self) -> None:
        self._fctHostControlData = FctHostControlData()
        self._testData = TestData()
        self._mainConfigData = MainConfigData()

    def save(self, fixtures: "list[Fixture]"):
        for fixture in fixtures:
            self.createOrUpdate(fixture)

    def createOrUpdate(self, fixture: Fixture):
        session = Session()
        fixtureDTO = (
            session.query(FixtureDTO).where(FixtureDTO.ip == fixture.ip).first()
        )
        if fixtureDTO == None:
            fixtureDTO = mapper.to(FixtureDTO).map(fixture)
            session.add(fixtureDTO)
        else:
            session.execute(
                update(FixtureDTO)
                .where(FixtureDTO.ip == fixture.ip)
                .values(
                    ip=fixture.ip,
                    areLastTestPass=fixture.areLastTestPass,
                    isSkipped=fixture.isSkipped,
                )
            )
            # fixtureDTO.ip = fixture.ip
            # fixtureDTO.areLastTestPass = fixture.areLastTestPass
            # fixtureDTO.isSkipped = fixture.isSkipped
        session.commit()
        Session.remove()

    def isSkipped(self, fixtureIp: str) -> bool:
        fixtureDTO = self.findDTO(fixtureIp)
        if fixtureDTO == None:
            return False
        else:
            return fixtureDTO.isSkipped

    def findDTO(self, fixtureIp: str) -> FixtureDTO:
        session = Session()
        data = session.query(FixtureDTO).where(FixtureDTO.ip == fixtureIp).first()
        session.close()
        Session.remove()
        return data

    def findAll(self) -> "list[Fixture]":
        fixtures = []
        for fixture in self._fctHostControlData.getAllFixtureConfigs():
            fixtures.append(self.find(fixture[FctHostControlData.PLC_IP_KEY]))
        return fixtures

    def find(self, fixtureIp: str) -> Fixture:
        for fixture in self._fctHostControlData.getAllFixtureConfigs():
            if fixtureIp == fixture[FctHostControlData.PLC_IP_KEY]:
                return Fixture(
                    fixture[FctHostControlData.PLC_ID_KEY],
                    fixtureIp,
                    self._testData.getYield(fixtureIp),
                    self._testData.areLastTestPass(fixtureIp),
                    self.isSkipped(fixtureIp),
                    self._mainConfigData.get_yield_error_min(),
                    self._mainConfigData.get_yield_warning_min(),
                )
