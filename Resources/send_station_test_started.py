#!/usr/bin/env python3
from FixtureSocketNotifier import FixtureSocketNotifier
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--ip", required=True, help="Fixture ip")
    args = parser.parse_args()

    print(f"\nSend Test Started: {__file__}\nargs: {vars(args)}")

    FixtureSocketNotifier().notify_test_start(fixtureIp=args.ip)
