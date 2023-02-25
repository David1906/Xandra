from Models.Test import Test
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import logging
import os
import sys


class GoogleSheet:
    SHEET_NAME = "FBT Bahubali"
    SCOPE = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.abspath(os.path.dirname(sys.argv[0]))
        + "/Static/yield-bahubali-f20f62671db6.json",
        SCOPE,
    )

    def add(self, test: Test):
        try:
            client = gspread.authorize(GoogleSheet.CREDENTIALS)
            sheet = client.open(GoogleSheet.SHEET_NAME).sheet1
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
