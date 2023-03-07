import unittest
from Tests.FixtureConfigTests import FixtureConfigTests
from Tests.FixtureTests import FixtureTests


# python -m unittest Tests
def suite():
    suite = unittest.TestSuite()
    suite.addTest(FixtureConfigTests())
    suite.addTest(FixtureTests())
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
