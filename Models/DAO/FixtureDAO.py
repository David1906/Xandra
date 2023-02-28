from sqlalchemy import Column, String, Integer, Float, Boolean
from DataAccess.SqlAlchemyBase import Base


class FixtureDAO(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True)
    ip = Column(String(64))
    isDisabled = Column(Boolean)
    isSkipped = Column(Boolean)

    def __init__(
        self,
        id: int = 0,
        ip: str = "",
        isDisabled: bool = False,
        isSkipped: bool = False,
    ):
        self.id = id
        self.ip = ip
        self.isDisabled = isDisabled
        self.isSkipped = isSkipped
