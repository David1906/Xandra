import json
from requests_futures.sessions import FuturesSession
from DataAccess.MainConfigData import MainConfigData


class XandraApiData:
    def __init__(self) -> None:
        self.mainConfigData = MainConfigData()

    def getYield(self, fixtureIp):
        session = FuturesSession()
        future = session.get(
            f"{self.mainConfigData.get_xandra_api_url()}/yield?fixtureIp={fixtureIp}&yieldCalcQty={self.mainConfigData.get_yield_calc_qty()}&lastTestPassQty={self.mainConfigData.get_last_test_pass_qty()}"
        )
        response = future.result()
        if response.status_code >= 200 and response.status_code < 300:
            responseTest = response.text
            return json.loads(responseTest)
