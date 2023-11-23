from datetime import datetime
from statemachine import State
import os


class TestStateMachineObserver:
    def __init__(self, sessionId: str, fixtureIp: str) -> None:
        self._sessionId = sessionId
        self._fixtureIp = fixtureIp

    def on_enter_state(self, event, state):
        msg = f"\n[{datetime.today()}] {self._sessionId} event: {event} to: {state.name}"
        f = open(f"state_machine_log_{self._fixtureIp}.txt", "a")
        f.write(msg)
        f.close()
        if os.environ.get("ENV") == "testing":
            print(msg)
