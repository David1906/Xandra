from Models.Fixture import Fixture
from Models.FixtureConfig import FixtureConfig
from Models.Test import Test
import unittest

# python -m unittest Tests/FixtureTests.py


class FixtureTests(unittest.TestCase):
    def test_is_affecting_yield_returns_true(self):
        cases = [
            (False, False, True),
            (False, False, False),
            (True, False, True),
        ]
        for isSkipped, isRetestMode, status in cases:
            result = self.call_is_affecting_yield(isSkipped, isRetestMode, status)
            self.assertTrue(
                result,
                f"isSkipped: {isSkipped}, isRetestMode: {isRetestMode}, status: {status}",
            )

    def test_is_affecting_yield_returns_false(self):
        cases = [
            (False, True, True),
            (False, True, False),
            (True, False, False),
            (True, True, True),
            (True, True, False),
        ]
        for isSkipped, isRetestMode, status in cases:
            result = self.call_is_affecting_yield(isSkipped, isRetestMode, status)
            self.assertFalse(
                result,
                f"isSkipped: {isSkipped}, isRetestMode: {isRetestMode}, status: {status}",
            )

    def call_is_affecting_yield(
        self, isSkipped: bool, isRetestMode: bool, status: bool
    ):
        fixtureConfig = FixtureConfig(isSkipped=isSkipped, isRetestMode=isRetestMode)
        test = Test(status=status)
        fixture = Fixture(fixtureConfig, test)
        return fixture.is_affecting_yield()

    def test_is_upload_to_sfc_returns_true(self):
        cases = [
            (True, True, True),
        ]
        result = True
        for isSkipped, isRetestMode, status in cases:
            result = self.call_is_upload_to_sfc(isSkipped, isRetestMode, status)
            self.assertTrue(
                result,
                f"isSkipped: {isSkipped}, isRetestMode: {isRetestMode}, status: {status}",
            )

    def test_is_upload_to_sfc_returns_false(self):
        cases = [
            (True, True, False),
            (True, False, False),
            (True, False, True),
            (False, False, False),
            (False, False, True),
        ]
        for isSkipped, isRetestMode, status in cases:
            result = self.call_is_upload_to_sfc(isSkipped, isRetestMode, status)
            self.assertFalse(
                result,
                f"isSkipped: {isSkipped}, isRetestMode: {isRetestMode}, status: {status}",
            )

    def call_is_upload_to_sfc(self, isSkipped: bool, isRetestMode: bool, status: bool):
        fixtureConfig = FixtureConfig(isSkipped=isSkipped, isRetestMode=isRetestMode)
        test = Test(status=status)
        fixture = Fixture(fixtureConfig, test)
        return fixture.is_upload_to_sfc()


if __name__ == "__main__":
    unittest.main()
