from DataAccess.SqlAlchemyBase import Session
from Models.Fixture import Fixture
from Models.DTO.FixtureDTO import FixtureDTO
from automapper import mapper


class FixtureData:
    def save(self, fixtures: "list[Fixture]"):
        for fixture in fixtures:
            self.createOrUpdate(fixture)

    def createOrUpdate(self, fixture: Fixture):
        session = Session()
        fixtureDTO = self.findDTO(fixture.ip)
        if fixtureDTO == None:
            fixtureDTO = mapper.to(FixtureDTO).map(fixture)
            session.add(fixtureDTO)
        else:
            fixtureDTO.ip = fixture.ip
            fixtureDTO.areLastTestPass = fixture.areLastTestPass
            fixtureDTO.isSkipped = fixture.isSkipped
        session.commit()
        session.close()

    def isSkipped(self, fixtureIp: str) -> bool:
        fixture = self.findOrDefault(fixtureIp)
        return fixture.isSkipped

    def findOrDefault(self, fixtureIp: str) -> Fixture:
        fixtureDTO = self.findDTO(fixtureIp)
        if fixtureDTO == None:
            return Fixture()
        else:
            return mapper.to(Fixture).map(fixtureDTO)

    def findDTO(self, fixtureIp: str) -> FixtureDTO:
        session = Session()
        data = session.query(FixtureDTO).where(FixtureDTO.ip == fixtureIp).first()
        session.close()
        return data
