from DataAccess.SqlAlchemyBase import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP


class FixtureStatusLogDAO(Base):
    __tablename__ = "fixture_status_logs"

    id = Column(Integer, primary_key=True)
    fixtureId = Column(Integer)
    fixtureIp = Column(String(64))
    status = Column(Integer)
    reason = Column(String(64))
    seconds = Column(Integer)
    timeStampStart = Column(TIMESTAMP)
    timeStampEnd = Column(TIMESTAMP)

    def __init__(
        self,
        fixtureId: int,
        fixtureIp: str,
        status: int,
        reason: str,
        seconds: int,
        timeStampStart: str,
        timeStampEnd: str,
    ) -> None:
        self.fixtureId = fixtureId
        self.fixtureIp = fixtureIp
        self.status = status
        self.reason = reason
        self.seconds = seconds
        self.timeStampStart = timeStampStart
        self.timeStampEnd = timeStampEnd
