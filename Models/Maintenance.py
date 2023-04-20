from datetime import datetime


class Maintenance:
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
        isNull: bool = False,
    ) -> None:
        self.id = id
        self.fixtureId = fixtureId
        self.fixtureIp = fixtureIp
        self.employee = employee
        self.dateTime = dateTime
        if dateTime == None:
            self.dateTime = datetime.now()
        self.part = part
        self.action = action
        self.description = description
        self.testId = testId
        self.resultStatus = resultStatus
        self.stepLabel = stepLabel
        self._isNull = isNull

    @property
    def isNull(self) -> bool:
        return self._isNull
