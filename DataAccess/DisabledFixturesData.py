import json


class DisabledFixturesData:
    DEFAULF_FILE_FULLPATH = "./disabled_fixtures.json"

    def __init__(self, fileFullPath=""):
        if fileFullPath != "":
            self.fileFullPath = fileFullPath
        else:
            self.fileFullPath = DisabledFixturesData.DEFAULF_FILE_FULLPATH

    def save(self, fixtures):
        disabledFixtures = {}
        for fixture in fixtures:
            disabledFixtures[fixture.ip] = fixture.isDisabled()
        json_string = json.dumps(disabledFixtures)
        with open(self.fileFullPath, "w") as outfile:
            json.dump(json_string, outfile)
