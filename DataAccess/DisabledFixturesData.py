import json
from DataAccess.MainConfigData import MainConfigData
from Models.Fixture import Fixture


class DisabledFixturesData:
    def __init__(self, fileFullPath: str = ""):
        self._mainConfigData = MainConfigData()

        if fileFullPath != "":
            self.fileFullPath = fileFullPath
        else:
            self.fileFullPath = self._mainConfigData.get_disabled_fixture_fullpath()

    def save(self, fixture: Fixture):
        disabledFixtures = {}
        disabledFixtures[fixture.ip] = fixture.isDisabled()
        with open(self.fileFullPath, "w") as outfile:
            json.dump(disabledFixtures, outfile)

    def update(self, fixture: Fixture):
        jsonFullpath = self._mainConfigData.get_disabled_fixture_fullpath()
        with open(jsonFullpath, "r") as jsonFile:
            data = json.load(jsonFile)

        data[fixture.ip] = fixture.isDisabled()

        with open(jsonFullpath, "w") as jsonFile:
            json.dump(data, jsonFile)
