from Core.Enums.TestStatus import TestStatus
from DataAccess.TestAnalyzer import TestAnalyzer
from Products.TestAnalyzerBuilder import TestAnalyzerBuilder
from statemachine import StateMachine
from statemachine.states import States
from typing import Any


class TestStateMachine(StateMachine):
    states = States.from_enum(TestStatus, initial=TestStatus.Initial)
    # fmt: off
    cycle = (
        states.Initial.to(states.Recovered, cond="can_recover")
        | states.Initial.to(states.Idle)
        | states.Recovered.to(states.PreTested, cond="is_board_loaded")
        | states.Recovered.to(states.Tested, cond="is_testing")
        | states.Recovered.to(states.Idle)

        | states.Idle.to(states.Initialized, cond="is_board_loaded")
        | states.Idle.to(states.Recovered, cond="is_testing")
        | states.Idle.to.itself(internal=True)

        | states.Initialized.to(states.PreTested)

        | states.PreTested.to(states.Tested, cond="is_testing")
        | states.PreTested.to(states.PreTestFailed, cond="is_failed")
        | states.PreTested.to(states.PreTestFailed, cond="is_board_released")
        | states.PreTested.to.itself()

        | states.PreTestFailed.to(states.Idle, cond="is_board_released")
        | states.PreTestFailed.to.itself(internal=True)

        | states.Tested.to(states.Finished, cond="is_finished")
        | states.Tested.to.itself()

        | states.Finished.to(states.Pass, cond="is_pass")
        | states.Finished.to(states.Failed, cond="is_failed")
        | states.Finished.to.itself(internal=True)

        | states.Pass.to(states.Released)
        | states.Failed.to(states.Released)

        | states.Released.to(states.Idle, cond="is_board_loaded")
        | states.Released.to(states.Idle, cond="is_board_released")
        | states.Released.to.itself(internal=True)
    )
    # fmt: on

    def __init__(
        self,
        model: Any = None,
        state_field: str = "state",
        start_value: Any = None,
        rtc: bool = True,
        allow_event_without_transition: bool = False,
        testAnalyzer: TestAnalyzer = None,
    ):
        super().__init__(
            model, state_field, start_value, rtc, allow_event_without_transition
        )
        self.testAnalyzer = (
            testAnalyzer
            if testAnalyzer != None
            else TestAnalyzerBuilder().build_based_on_main_config()
        )

    def can_recover(self):
        return self.testAnalyzer.can_recover()

    def is_board_loaded(self):
        return self.testAnalyzer.is_board_loaded()

    def is_testing(self):
        return self.testAnalyzer.is_testing()

    def is_finished(self):
        return self.testAnalyzer.is_finished()

    def is_board_released(self):
        return self.testAnalyzer.is_board_released()

    def is_pass(self):
        return self.testAnalyzer.is_pass()

    def is_failed(self):
        return self.testAnalyzer.is_failed()
