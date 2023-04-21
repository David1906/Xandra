from DataAccess.SqlAlchemyBase import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, Boolean


class FixtureStatusLogDTO(Base):
    __tablename__ = "fixture_status_logs"

    id = Column(Integer, primary_key=True)
    fixtureId = Column(Integer)
    fixtureIp = Column(String(64))
    status = Column(Integer)
    reason = Column(String(64))
    seconds = Column(Integer)
    timeStampStart = Column(TIMESTAMP)
    timeStampEnd = Column(TIMESTAMP)
    isSync = Column(Boolean)

    def __init__(
        self,
        fixtureId: int = 0,
        fixtureIp: str = "",
        status: int = 0,
        reason: str = "",
        seconds: int = 0,
        timeStampStart: str = "",
        timeStampEnd: str = "",
        isSync: bool = False,
    ) -> None:
        self.fixtureId = fixtureId
        self.fixtureIp = fixtureIp
        self.status = status
        self.reason = reason
        self.seconds = seconds
        self.timeStampStart = timeStampStart
        self.timeStampEnd = timeStampEnd
        self.isSync = isSync
