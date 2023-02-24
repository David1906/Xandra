from sqlalchemy import Column, String, Integer, Float, Boolean
from DataAccess.SqlAlchemyBase import Base


class FixtureDTO(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True)
    ip = Column(String(64))
    areLastTestPass = Column(Boolean)
    isSkipped = Column(Boolean)

    def __init__(
        self,
        id: int = 0,
        ip: str = "",
        yieldRate: float = 0,
        areLastTestPass: bool = False,
        isSkipped: bool = False,
    ):
        self.id = id
        self.ip = ip
        self.yieldRate = yieldRate
        self.areLastTestPass = areLastTestPass
        self.isSkipped = isSkipped
