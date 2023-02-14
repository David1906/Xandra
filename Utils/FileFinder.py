import glob, os, re
from datetime import datetime, date, timedelta


class FileFinder:
    def __init__(self, fullPath) -> None:
        self.fullPath = fullPath

    def getFilesYoungerThan(
        self,
        days=0,
    ):
        dt = self.getDateTimeAgo(days=days)
        return list(
            filter(lambda file: self.older(file, dt), glob.iglob(self.fullPath))
        )

    def getDateTimeAgo(self, days=0, weeks=0) -> datetime:
        dateAgo = date.today() - timedelta(days=days, weeks=weeks)
        return datetime.combine(dateAgo, datetime.min.time())

    def older(self, file, dateTime) -> bool:
        result = os.path.getmtime(file) > dateTime.timestamp()
        return result


# PXE IP : 10.12.206.107
REGEX_FIXTURE_IP = "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
REGEX_FIXTURE_IP = f"^FixtureIP\s*:\s*{REGEX_FIXTURE_IP}"
REGEX_RESULT = "^result\s*:(pass|failed)+"
REGEX_PASS = "pass"


def finder(fullPath):
    with open(fullPath, "r") as fp:
        result = None
        fixtureIp = None
        for l_no, line in enumerate(fp):
            if result == None and re.search(REGEX_RESULT, line, re.IGNORECASE):
                result = re.search(REGEX_PASS, line, re.IGNORECASE) != None
            if fixtureIp == None and re.search(REGEX_FIXTURE_IP, line, re.IGNORECASE):
                match = re.findall(REGEX_FIXTURE_IP, line)
                if match != None:
                    fixtureIp = match[0]
            if result != None and fixtureIp != None:
                break
        print(f"fixtureIp: {fixtureIp}      result: {result}")


filePath = "./Resources/test_logs/*.*"
files = FileFinder(filePath).getFilesYoungerThan(days=20)
for file in files:
    finder(file)
