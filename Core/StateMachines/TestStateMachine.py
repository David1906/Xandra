from typing import Any
from Core.Enums.TestStatus import TestStatus
from statemachine import StateMachine
from statemachine.states import States


class TestStateMachine(StateMachine):
    states = States.from_enum(TestStatus, initial=TestStatus.Initialized)

    idle = states.Initialized.to(states.Idle) | states.Idle.to.itself(internal=True)
    loadboard = (
        states.Idle.to(states.BoardLoaded)
        | states.Initialized.to(states.BoardLoaded)
        | states.BoardLoaded.to.itself(internal=True)
    )
    test = (
        states.BoardLoaded.to(states.Tested)
        | states.Initialized.to(states.Tested)
        | states.Tested.to.itself()
    )
    finish = states.Tested.to(states.Finished) | states.Finished.to.itself(
        internal=True
    )
    release = (
        states.Finished.to(states.Idle)
        | states.Initialized.to(states.Idle)
        | states.BoardLoaded.to(states.Idle)
        | states.Tested.to(states.Idle)
        | states.Idle.to.itself(internal=True)
    )

    def can_load_board(self) -> bool:
        return self.current_state.value in [
            TestStatus.Initialized.value,
            TestStatus.Idle.value,
        ]

    def can_test(self) -> bool:
        return self.current_state.value in [
            TestStatus.Initialized.value,
            TestStatus.BoardLoaded.value,
            TestStatus.Tested.value,
        ]

    def can_finish(self) -> bool:
        return self.current_state.value == TestStatus.Tested.value

    def can_idle(self) -> bool:
        return self.current_state.value in [
            TestStatus.Finished.value,
            TestStatus.Tested.value,
            TestStatus.BoardLoaded.value,
            TestStatus.Initialized.value,
        ]
