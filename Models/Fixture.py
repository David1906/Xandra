from Models.FixtureConfig import FixtureConfig
from Models.Test import Test
from timeit import default_timer as timer
import datetime
import math


class Fixture:
    def __init__(self, fixtureConfig: FixtureConfig, test: Test = None) -> None:
        self._fixtureConfig = fixtureConfig
        self._test = test or Test(isNull=True)
        self.hasErrorUploadingToSfc = False
        self.errorMsg = ""
        self.startTimer = timer()

    def get_status_string(self):
        if self._test.isNull:
            elapsedTime = ""
            if self._fixtureConfig.isTesting:
                elapsedTime = f"... ({self.get_elapsed_time()})"
            return f"Status: {self._fixtureConfig.get_status_text()}{elapsedTime}"
        error = "(Upload SFC Error)" if self.hasErrorUploadingToSfc else ""
        mode = f"{error}" if self.is_online() else "(Offline)"
        return f"SN: {self._test.serialNumber}      Result: {self._test.get_result_string()} {mode}"

    def get_elapsed_time(self) -> str:
        return str(datetime.timedelta(seconds=math.floor(timer() - self.startTimer)))

    def is_online(self) -> bool:
        return self.is_upload_to_sfc() or not self._fixtureConfig.isSkipped

    def is_upload_to_sfc(self) -> bool:
        return (
            self._test.status
            and self._fixtureConfig.isRetestMode
            and self._fixtureConfig.isSkipped
        )

    def is_affecting_yield(self) -> bool:
        if self._test.status:
            return not self._fixtureConfig.isRetestMode
        else:
            return (
                not self._fixtureConfig.isSkipped
                and not self._fixtureConfig.isRetestMode
            )

    def is_retest_mode(self) -> bool:
        return self._fixtureConfig.isRetestMode

    def is_skipped(self) -> bool:
        return self._fixtureConfig.isSkipped

    def get_yield(self) -> float:
        return self._fixtureConfig.yieldRate

    def get_ip(self) -> str:
        return self._fixtureConfig.ip

    def get_id(self) -> str:
        return self._fixtureConfig.id

    def get_are_last_test_pass(self) -> bool:
        return self._fixtureConfig.areLastTestPass

    def is_disabled(self) -> bool:
        return self._fixtureConfig.is_disabled()

    def get_status_color(self) -> bool:
        return self._fixtureConfig.get_status_color()

    def set_test(self, test: Test):
        self.hasErrorUploadingToSfc = False
        self.errorMsg = ""
        self._test = test

    def equals(self, fixture) -> bool:
        return fixture.get_id() == self.get_id()

    def equalsIp(self, fixtureIp: str) -> bool:
        return self._fixtureConfig.ip == fixtureIp

    def set_isTesting(self, value: bool):
        self._fixtureConfig.isTesting = value
        if value:
            self._test = Test(isNull=True)
            self.startTimer = timer()
            self.errorMsg = ""

    def get_config(self) -> FixtureConfig:
        return self._fixtureConfig

    def reset(self):
        self._fixtureConfig.reset()

    def set_reset_mode(self, value: bool):
        self._fixtureConfig.isRetestMode = value

    def set_skipped(self, value: bool):
        self._fixtureConfig.isSkipped = value

    def set_config(self, fixtureConfig: FixtureConfig):
        self._fixtureConfig = fixtureConfig
