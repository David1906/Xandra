import json
from DataAccess.MainConfigData import MainConfigData


class DisabledFixturesData:
    def __init__(self, fileFullPath=""):
        if fileFullPath != "":
            self.fileFullPath = fileFullPath
        else:
            self.fileFullPath = MainConfigData().get_disabled_fixture_fullpath()

    def save(self, fixtures):
        disabledFixtures = {}
        for fixture in fixtures:
            disabledFixtures[fixture.ip] = fixture.isDisabled()
        with open(self.fileFullPath, "w") as outfile:
            json.dump(disabledFixtures, outfile)
