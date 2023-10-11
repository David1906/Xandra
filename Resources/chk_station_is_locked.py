#!/usr/bin/env python3
from HttpClient import HttpClient
import os

httpClient = HttpClient(resultFileName="chk_station_is_disabled.result")
if not httpClient.is_locked(fixtureIp=os.getenv("XANDRA_FIXTURE_IP")):
    exit(1)
else:
    exit(0)
