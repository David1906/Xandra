from cgi import test
import json
from requests_futures.sessions import FuturesSession
from DataAccess.MainConfigData import MainConfigData


class XandraApiData:
    def __init__(self) -> None:
        self.mainConfigData = MainConfigData()

    def getYield(self, fixtureIp: str) -> "list[test]":
        return self.get(
            f"{self.mainConfigData.get_xandra_api_url()}/yield?fixtureIp={fixtureIp}&yieldCalcQty={self.mainConfigData.get_yield_calc_qty()}&lastTestPassQty={self.mainConfigData.get_last_test_pass_qty()}"
        )

    def getLastTests(self, fixtureIp: str) -> "list[test]":
        response = self.get(
            f"{self.mainConfigData.get_xandra_api_url()}/tests?fixtureIp={fixtureIp}&qty={self.mainConfigData.get_yield_calc_qty()}"
        )
        return response["data"]

    def getLastFailures(self, fixtureIp: str) -> "list[test]":
        response = self.get(
            f"{self.mainConfigData.get_xandra_api_url()}/failures?fixtureIp={fixtureIp}&qty={self.mainConfigData.get_yield_calc_qty()}"
        )
        return response["data"]

    def get(self, uri: str) -> "list[test]":
        session = FuturesSession()
        future = session.get(uri)
        response = future.result()
        if response.status_code >= 200 and response.status_code < 300:
            responseTest = response.text
            return json.loads(responseTest)
