from datetime import datetime
import re


class Test:
    ALLOWED_EXTENSIONS = [".log"]

    def __init__(
        self,
        id: int = None,
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
        mode: int = 0,
    ) -> None:
        self.id = id
        self.serialNumber = serialNumber
        self.project = project
        self.operator = operator
        self.startTime = startTime
        self.endTime = endTime
        self.codeVersion = codeVersion
        self.fixtureIp = fixtureIp
        self.status = status
        self.stepLabel = stepLabel
        self.description = description
        self.mode = mode
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
            if self.is_dimm_error() or self.is_chk_serialuart_error():
                shortDescription = " - " + self.get_short_description()
            return f"FAIL - {self.stepLabel}{shortDescription}"

    def is_dimm_error(self) -> bool:
        match = re.search("chk_sel|apos_chk_k2", self.stepLabel, re.IGNORECASE)
        return match != None

    def is_chk_serialuart_error(self) -> bool:
        match = re.search("chk_serialuart", self.stepLabel, re.IGNORECASE)
        return match != None

    def get_short_description(self):
        if re.search("memory error", self.description, re.IGNORECASE):
            return "DIMM Error"
        if re.search("voltage", self.description, re.IGNORECASE):
            match = re.search("Voltage SYS_\w+", self.description, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        if re.search("uart", self.description, re.IGNORECASE):
            match = re.search("TTYUSB\w+", self.description, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return "unknown"
