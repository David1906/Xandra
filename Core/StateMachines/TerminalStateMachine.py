from typing import Any
from DataAccess.TerminalAnalyzer import TerminalAnalyzer
from Products.TerminalAnalyzerBuilder import TerminalAnalyzerBuilder
from statemachine import State, StateMachine
from statemachine.states import States
import enum


class TemrinalStatus(enum.Enum):
    Stopped = 1
    IDLE = 2
    Loaded = 3
    PoweredOn = 4
    Tested = 5
    Finished = 6
    Released = 7


class TerminalStateMachine(StateMachine):
    states = States.from_enum(TemrinalStatus, initial=TemrinalStatus.Stopped)
    cycle = (
        states.Stopped.to(states.IDLE, cond="can_start")
        | states.Stopped.to.itself()
        | states.IDLE.to(states.Loaded, cond="is_board_loaded")
        | states.IDLE.to.itself()
        | states.Loaded.to(states.Stopped, cond="is_stopped")
        | states.Loaded.to(states.PoweredOn, cond="is_power_on")
        | states.Loaded.to(states.Finished, cond="is_finished")
        | states.Loaded.to.itself()
        | states.PoweredOn.to(states.Stopped, cond="is_stopped")
        | states.PoweredOn.to(states.Tested, cond="is_testing")
        | states.PoweredOn.to(states.Finished, cond="is_finished")
        | states.PoweredOn.to.itself()
        | states.Tested.to(states.Stopped, cond="is_stopped")
        | states.Tested.to(states.Finished, cond="is_finished")
        | states.Tested.to.itself()
        | states.Finished.to(states.Released)
        | states.Released.to(states.Stopped, cond="is_fixture_released")
        | states.Released.to(states.IDLE, cond="is_fixture_released")
        | states.Released.to.itself()
    )

    def __init__(
        self,
        model: Any = None,
        state_field: str = "state",
        start_value: Any = None,
        rtc: bool = True,
        allow_event_without_transition: bool = False,
        terminalAnalyzer: TerminalAnalyzer = None,
    ):
        super().__init__(
            model, state_field, start_value, rtc, allow_event_without_transition
        )
        self._isStopped = False
        self._canStart = False
        self.terminalAnalyzer = (
            terminalAnalyzer
            if terminalAnalyzer != None
            else TerminalAnalyzerBuilder().build_based_on_main_config()
        )

    def before_cycle(self, event: str, source: State, target: State, message: str = ""):
        print("Cycle", target)

    def is_board_loaded(self):
        return self.terminalAnalyzer.is_board_loaded()

    def is_power_on(self):
        return self.terminalAnalyzer.is_power_on()

    def is_finished(self):
        return self.terminalAnalyzer.is_finished()

    def is_testing(self):
        return self.terminalAnalyzer.is_testing()

    def is_testing(self):
        return self.terminalAnalyzer.is_testing()

    def is_fixture_released(self):
        return self.terminalAnalyzer.is_fixture_released()

    def is_stopped(self):
        return self._isStopped

    def can_start(self):
        return self._canStart

    def stop(self):
        self._isStopped = True

    def reset(self):
        self._isStopped = False
        self._canStart = True
