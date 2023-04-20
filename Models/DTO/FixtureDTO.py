from Core.Enums.FixtureMode import FixtureMode
from DataAccess.SqlAlchemyBase import Base
from sqlalchemy import Column, String, Integer, Boolean


class FixtureDTO(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True)
    ip = Column(String(64))
    abortTest = Column(Boolean)
    isDisabled = Column(Boolean)
    isSkipped = Column(Boolean)
    isRetestMode = Column(Boolean)
    enableLock = Column(Boolean)
    mode = Column(Integer)

    def __init__(
        self,
        id: int = 0,
        ip: str = "",
        abortTest: bool = False,
        isDisabled: bool = False,
        isSkipped: bool = False,
        isRetestMode: bool = False,
        enableLock: bool = False,
        mode: int = FixtureMode.UNKNOWN.value,
    ):
        self.id = id
        self.ip = ip
        self.abortTest = abortTest
        self.isDisabled = isDisabled
        self.isSkipped = isSkipped
        self.isRetestMode = isRetestMode
        self.enableLock = enableLock
        self.mode = mode
