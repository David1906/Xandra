from DataAccess.MainConfigData import MainConfigData
from Models.Test import Test
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import logging


class GoogleSheet:
    SCOPE = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self) -> None:
        self._mainConfigData = MainConfigData()
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self._mainConfigData.get_google_keyfilePath(),
            GoogleSheet.SCOPE,
        )

    def add(self, test: Test):
        try:
            if not self._mainConfigData.get_google_isActivated():
                return
            client = gspread.authorize(self.credentials)
            sheet = client.open(self._mainConfigData.get_google_sheetName()).sheet1
            sheet.append_row(
                [
                    "",
                    test.serialNumber,
                    test.project,
                    test.startTime.strftime("%d/%m/%Y %H:%M:%S"),
                    test.endTime.strftime("%d/%m/%Y %H:%M:%S"),
                    test.codeVersion,
                    test.fixtureIp,
                    "PASS" if test.status else "FAILED",
                    test.stepLabel,
                    test.operator,
                ],
                value_input_option="USER_ENTERED",
            )
        except Exception as e:
            logging.error("Error appending google sheet. " + str(e))
