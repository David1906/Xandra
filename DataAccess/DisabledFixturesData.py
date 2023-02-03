import json
from DataAccess.MainConfigData import MainConfigData


class DisabledFixturesData:
    def __init__(self, fileFullPath=""):
        self._mainConfigData = MainConfigData()

        if fileFullPath != "":
            self.fileFullPath = fileFullPath
        else:
            self.fileFullPath = self._mainConfigData.get_disabled_fixture_fullpath()

    def save(self, fixtures):
        disabledFixtures = {}
        for fixture in fixtures:
            disabledFixtures[fixture.ip] = fixture.isDisabled()
        with open(self.fileFullPath, "w") as outfile:
            json.dump(disabledFixtures, outfile)

    def update(self, fixture):
        jsonFullpath = self._mainConfigData.get_disabled_fixture_fullpath()
        with open(jsonFullpath, "r") as jsonFile:
            data = json.load(jsonFile)

        data[fixture.ip] = fixture.isDisabled()

        with open(jsonFullpath, "w") as jsonFile:
            json.dump(data, jsonFile)
