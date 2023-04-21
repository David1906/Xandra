from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from DataAccess.SqlAlchemyBase import Base


class MaintenanceDTO(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True)
    fixtureId = Column(Integer)
    fixtureIp = Column(String(64))
    employee = Column(Integer)
    dateTime = Column(DateTime)
    part = Column(String(512))
    action = Column(String(512))
    description = Column(String(512))
    testId = Column(Integer)
    resultStatus = Column(Boolean)
    stepLabel = Column(String(512))
    isSync = Column(Boolean)

    def __init__(
        self,
        id: int = None,
        fixtureId: int = "",
        fixtureIp: str = "",
        employee: int = "",
        dateTime: datetime = None,
        part: str = "",
        action: str = "",
        description: str = "",
        testId: int = None,
        resultStatus: bool = None,
        stepLabel: str = "",
        isSync: bool = False,
    ) -> None:
        self.id = id
        self.fixtureId = fixtureId
        self.fixtureIp = fixtureIp
        self.employee = employee
        self.dateTime = dateTime
        self.part = part
        self.action = action
        self.description = description
        self.testId = testId
        self.resultStatus = resultStatus
        self.stepLabel = stepLabel
        self.isSync = isSync
