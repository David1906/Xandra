#!/usr/bin/env python3
from FixtureSocketNotifier import FixtureSocketNotifier
import os


if FixtureSocketNotifier(resultFileName="chk_station_yield.result").is_locked(
    fixtureIp=os.getenv("XANDRA_FIXTURE_IP")
):
    exit(0)
else:
    exit(1)
