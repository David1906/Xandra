from Models.Test import Test


class NullTest(Test):
    def __init__(self) -> None:
        super().__init__(isNull=True)
