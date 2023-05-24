#!/usr/bin/env python3
from FixtureSocketNotifier import FixtureSocketNotifier
import os

fixtureSocketNotifier = FixtureSocketNotifier(resultFileName="chk_station_yield.result")
if fixtureSocketNotifier.is_locked(fixtureIp=os.getenv("XANDRA_FIXTURE_IP")):
    exit(0)
else:
    fixtureSocketNotifier.notify_finish(fixtureIp=os.getenv("XANDRA_FIXTURE_IP"))
    exit(1)
