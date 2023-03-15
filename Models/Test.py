from datetime import datetime
import re


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
        isNull: bool = False,
        description: str = None,
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
        self.description = description
        self.fullPath = fullPath
        self.isNull = isNull

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
            return "PASS"
        else:
            shortDescription = ""
            if self.is_chk_sel_error():
                shortDescription = " - " + self.get_short_description()
            return f"FAIL - {self.stepLabel}{shortDescription}"

    def is_chk_sel_error(self) -> bool:
        match = re.search(self.stepLabel, "chk_sel", re.IGNORECASE)
        return match != None

    def get_short_description(self):
        if re.search("memory error", self.description, re.IGNORECASE):
            return "DIMM Error"
        if re.search("voltage", self.description, re.IGNORECASE):
            match = re.search("Voltage SYS_\w+", self.description, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return "unknown"
