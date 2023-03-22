from Models.Fixture import Fixture
from Models.FixtureConfig import FixtureConfig
from Models.Test import Test
import unittest

# python -m unittest Tests/FixtureConfigTests.py


class FixtureConfigTests(unittest.TestCase):
    def test_is_disabled_returns_true(self):
        cases = [
            FixtureConfig(
                isSkipped=False,
                isRetestMode=False,
                areLastTestPass=False,
                yieldRate=0,
                yieldErrorMin=70,
            ),
            FixtureConfig(
                isSkipped=True,
                isRetestMode=True,
                areLastTestPass=False,
                yieldRate=0,
                yieldErrorMin=70,
            ),
            FixtureConfig(
                isSkipped=False,
                isRetestMode=False,
                areLastTestPass=False,
                areLastTestFail=True,
                yieldRate=100,
                yieldErrorMin=70,
            ),
        ]
        for fixtureConfig in cases:
            result = fixtureConfig.is_disabled()
            self.assertTrue(
                result,
                str(fixtureConfig),
            )

    def test_is_disabled_returns_false(self):
        cases = [
            FixtureConfig(
                isSkipped=False,
                isRetestMode=False,
                areLastTestPass=False,
                yieldRate=100,
                yieldErrorMin=70,
            ),
            FixtureConfig(
                isSkipped=True,
                isRetestMode=True,
                areLastTestPass=False,
                yieldRate=100,
                yieldErrorMin=70,
            ),
            FixtureConfig(
                isSkipped=True,
                isRetestMode=False,
                areLastTestPass=True,
                yieldRate=0,
                yieldErrorMin=70,
            ),
            FixtureConfig(
                isSkipped=False,
                isRetestMode=False,
                areLastTestPass=False,
                areLastTestFail=False,
                yieldRate=100,
                yieldErrorMin=70,
            ),
            FixtureConfig(
                isSkipped=False,
                isRetestMode=False,
                areLastTestPass=True,
                areLastTestFail=True,
                yieldRate=0,
                yieldErrorMin=70,
            ),
        ]
        for fixtureConfig in cases:
            result = fixtureConfig.is_disabled()
            self.assertFalse(
                result,
                str(fixtureConfig),
            )

    def test_lock_enabled_returns_true(self):
        cases = [
            FixtureConfig(isSkipped=False, isRetestMode=True),
            FixtureConfig(isSkipped=False, isRetestMode=False),
            FixtureConfig(isSkipped=True, isRetestMode=True),
        ]
        for fixtureConfig in cases:
            result = fixtureConfig.is_lock_enabled()
            self.assertTrue(
                result,
                str(fixtureConfig),
            )

    def test_lock_enabled_returns_false(self):
        cases = [
            FixtureConfig(isSkipped=True, isRetestMode=False),
        ]
        for fixtureConfig in cases:
            result = fixtureConfig.is_lock_enabled()
            self.assertFalse(
                result,
                str(fixtureConfig),
            )


if __name__ == "__main__":
    unittest.main()
