from Models.Maintenance import Maintenance


class NullMaintenance(Maintenance):
    def __init__(self) -> None:
        super().__init__(
            fixtureId=0, fixtureIp="", part="", employee="", description="", isNull=True
        )
