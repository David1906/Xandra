from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from DataAccess.SqlAlchemyBase import Base


class TestDTO(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True)
    serialNumber = Column(String(512))
    project = Column(String(512))
    startTime = Column(DateTime)
    endTime = Column(DateTime)
    codeVersion = Column(String(512))
    fixtureIp = Column(String(64))
    status = Column(Boolean)
    stepLabel = Column(String(512))
    operator = Column(String(512))
    fullPath = Column(String(2048))
    uploadToSFC = Column(Boolean)
    description = Column(String(2048))
    mode = Column(Integer)
    isSync = Column(Boolean)

    def __init__(
        self,
        id: int = None,
        serialNumber: str = None,
        project: str = None,
        startTime: datetime = None,
        endTime: datetime = None,
        codeVersion: str = None,
        fixtureIp: str = None,
        status: bool = False,
        stepLabel: str = None,
        operator: str = None,
        fullPath: str = None,
        uploadToSFC: bool = False,
        description: str = None,
        mode: int = None,
        isSync: bool = False,
    ) -> None:
        self.id = id
        self.serialNumber = serialNumber
        self.project = project
        self.startTime = startTime
        self.endTime = endTime
        self.codeVersion = codeVersion
        self.fixtureIp = fixtureIp
        self.status = status
        self.stepLabel = stepLabel
        self.operator = operator
        self.fullPath = fullPath
        self.uploadToSFC = uploadToSFC
        self.description = description
        self.mode = mode
        self.isSync = isSync
