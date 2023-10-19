from abc import ABC, abstractmethod
from Models.NullTerminalAnalysis import NullTerminalAnalysis
from Models.TerminalAnalysis import TerminalAnalysis
from typing import Tuple
import subprocess


class TerminalAnalyzer(ABC):
    ERROR_ID = -1
    DELETE_NEW_LINE_PIPE = "| tr --delete '\n'"

    def __init__(self, sessionId: str) -> None:
        self.sessionId = sessionId
        self.prevLastLine = ""
        self.currentAnalysis = NullTerminalAnalysis()

    @abstractmethod
    def is_board_loaded(self) -> bool:
        pass

    @abstractmethod
    def is_power_on(self) -> bool:
        pass

    @abstractmethod
    def refresh_serial_number(self) -> str:
        pass

    @abstractmethod
    def is_finished(self) -> bool:
        pass

    @abstractmethod
    def is_testing(self) -> bool:
        pass

    @abstractmethod
    def get_test_item(self) -> str:
        pass

    @abstractmethod
    def is_result_parsed(self) -> bool:
        pass

    @abstractmethod
    def is_stopped(self) -> bool:
        pass

    @abstractmethod
    def get_finished_terminalAnalysis(self) -> TerminalAnalysis:
        pass

    def buffer_contains(self, regex: str) -> bool:
        p1 = subprocess.Popen(
            ["tmux", "capture-pane", "-t", self.sessionId, "-pS", "-"],
            stdout=subprocess.PIPE,
        )
        p2 = subprocess.Popen(
            ["grep", "-Poi", regex], stdin=p1.stdout, stdout=subprocess.PIPE
        )
        p1.stdout.close()
        p2.communicate()
        return p2.returncode == 0

    def buffer_extract(self, regex: str, multiline: bool = False) -> Tuple[int, str]:
        match = subprocess.getoutput(
            f'{self._get_tmux_capture_cmd()} {self.DELETE_NEW_LINE_PIPE if multiline else ""} | grep -Poin "{regex}" | tail -1'
        )
        return self.match_to_touple(match)

    def match_to_touple(self, match: str) -> Tuple[int, str]:
        try:
            matchSplited = match.split(":", 2)
            lineNo = 0
            if len(matchSplited) > 0:
                lineNo = int(matchSplited[0])
            value = ""
            if len(matchSplited) > 1:
                value = matchSplited[1].strip()
            return (lineNo, value)
        except:
            return (self.ERROR_ID, "")

    def has_changed(self):
        currentLastLine = subprocess.getoutput(
            f"{self._get_tmux_capture_cmd()} | tail -15"
        )
        hasChanged = currentLastLine != self.prevLastLine
        self.prevLastLine = currentLastLine
        return hasChanged

    def _get_tmux_capture_cmd(self):
        return f"tmux capture-pane -t {self.sessionId} -pS -"
