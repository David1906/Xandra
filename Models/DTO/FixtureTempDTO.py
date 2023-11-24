from datetime import datetime
from DataAccess.SqlAlchemyBase import Base
from sqlalchemy import Column, Float, Integer, TIMESTAMP


class FixtureTempDTO(Base):
    __tablename__ = "fixture_temp"

    id = Column(Integer, primary_key=True)
    fixtureId = Column(Integer)
    temp = Column(Float)
    timeStamp = Column(TIMESTAMP)

    def __init__(
        self,
        fixtureId: int = 0,
        temp: float = 0.0,
        timeStamp: datetime = None,
    ) -> None:
        self.fixtureId = fixtureId
        self.temp = temp
        self.timeStamp = timeStamp
