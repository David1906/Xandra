class Interval:
    def __init__(self, min: int, max: int) -> None:
        self.min = min
        self.max = max

    def normalize(self, value: int) -> int:
        if value > self.max:
            return self.max
        elif value < self.min:
            return self.min
        return value
