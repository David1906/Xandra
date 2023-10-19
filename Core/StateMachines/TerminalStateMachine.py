from typing import Any
from DataAccess.TerminalAnalyzer import TerminalAnalyzer
from Products.TerminalAnalyzerBuilder import TerminalAnalyzerBuilder
from statemachine import StateMachine
from statemachine.states import States
import enum


class TemrinalStatus(enum.Enum):
    IDLE = 0
    Loaded = 1
    PoweredOn = 2
    Tested = 3
    Finished = 4


class TerminalStateMachine(StateMachine):
    states = States.from_enum(TemrinalStatus, initial=TemrinalStatus.IDLE)
    cycle = (
        states.IDLE.to(states.Loaded, cond="is_board_loaded")
        | states.IDLE.to.itself()
        | states.Loaded.to(states.IDLE, cond="is_stopped")
        | states.Loaded.to(states.PoweredOn, cond="is_power_on")
        | states.Loaded.to(states.Finished, cond="is_finished")
        | states.Loaded.to.itself()
        | states.PoweredOn.to(states.IDLE, cond="is_stopped")
        | states.PoweredOn.to(states.Tested, cond="is_testing")
        | states.PoweredOn.to(states.Finished, cond="is_finished")
        | states.PoweredOn.to.itself()
        | states.Tested.to(states.IDLE, cond="is_stopped")
        | states.Tested.to(states.Finished, cond="is_finished")
        | states.Tested.to.itself()
        | states.Finished.to(states.IDLE)
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
        self.terminalAnalyzer = (
            terminalAnalyzer
            if terminalAnalyzer != None
            else TerminalAnalyzerBuilder().build_based_on_main_config()
        )

    def is_board_loaded(self):
        return self.terminalAnalyzer.is_board_loaded()

    def is_power_on(self):
        return self.terminalAnalyzer.is_power_on()

    def is_finished(self):
        return self.terminalAnalyzer.is_finished()

    def is_testing(self):
        return self.terminalAnalyzer.is_testing()

    def is_result_parsed(self):
        return self.terminalAnalyzer.is_result_parsed()

    def is_stopped(self):
        return self.terminalAnalyzer.is_stopped()
