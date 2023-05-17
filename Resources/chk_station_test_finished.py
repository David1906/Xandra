#!/usr/bin/env python3

import os
from FixtureSocketNotifier import FixtureSocketNotifier


FixtureSocketNotifier().notify_finish(fixtureIp=os.getenv("XANDRA_FIXTURE_IP"))
exit(0)
