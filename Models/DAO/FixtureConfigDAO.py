from sqlalchemy import Column, String, Integer, Boolean
from DataAccess.SqlAlchemyBase import Base


class FixtureConfigDAO(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True)
    ip = Column(String(64))
    isDisabled = Column(Boolean)
    isSkipped = Column(Boolean)
    isRetestMode = Column(Boolean)
    enableLock = Column(Boolean)

    def __init__(
        self,
        id: int = 0,
        ip: str = "",
        isDisabled: bool = False,
        isSkipped: bool = False,
        isRetestMode: bool = False,
        enableLock: bool = False,
    ):
        self.id = id
        self.ip = ip
        self.isDisabled = isDisabled
        self.isSkipped = isSkipped
        self.isRetestMode = isRetestMode
        self.enableLock = enableLock
