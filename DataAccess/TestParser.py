from abc import ABC, abstractmethod
from Models.Test import Test


class TestParser(ABC):
    @abstractmethod
    def parse(self) -> Test:
        pass
