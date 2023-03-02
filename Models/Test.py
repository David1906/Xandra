from datetime import datetime


class Test:
    def __init__(
        self,
        serialNumber: str = None,
        project: str = None,
        startTime: datetime = None,
        endTime: datetime = None,
        codeVersion: str = None,
        fixtureIp: str = None,
        status: bool = None,
        stepLabel: str = None,
        operator: str = None,
        fullPath: str = None,
        countInYield: bool = False,
        uploadToSFC: bool = False,
        sfcError: bool = False,
    ) -> None:
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
        self.countInYield = countInYield
        self.uploadToSFC = uploadToSFC
        self.sfcError = sfcError

    def is_complete(self) -> bool:
        return (
            self.serialNumber != None
            and self.project != None
            and self.startTime != None
            and self.endTime != None
            and self.codeVersion != None
            and self.fixtureIp != None
            and self.status != None
            and self.stepLabel != None
            and self.operator != None
        )

    def get_result_string(self) -> str:
        if self.status:
            return "PASS" + (" (SFC Upload Error)" if self.sfcError else "")
        else:
            return f"FAIL - {self.stepLabel}"
