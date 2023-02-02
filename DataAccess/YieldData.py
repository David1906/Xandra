import json
import random


class YieldData:
    YIELD_JSON_PATH = "./Resources/yield.json"

    def get_yield(self, ip):
        return self._getValue(ip)

    def _getValue(self, key):
        with open(YieldData.YIELD_JSON_PATH) as json_file:
            data = json.load(json_file)
            if type(data) is dict:
                if key in data:
                    return data[key]
        return ""
