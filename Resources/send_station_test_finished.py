#!/usr/bin/env python3
from FixtureSocketNotifier import FixtureSocketNotifier
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--ip", required=True, help="Fixture ip")
    parser.add_argument("--sn", required=True, help="Serial number of the tested board")
    parser.add_argument("--ln", required=True, help="File name of the test log")
    parser.add_argument("--ct", required=True, help="Current test name")
    args = parser.parse_args()

    print(f"\nSend Test Finished: {__file__}\nargs: {vars(args)}")

    FixtureSocketNotifier().notify_finish(
        fixtureIp=args.ip,
        serialNumber=args.sn,
        logFileName=args.ln,
        currentTest=args.ct,
    )
