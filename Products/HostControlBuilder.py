from DataAccess.HostControl import HostControl
from DataAccess.MainConfigDAO import MainConfigDAO
from Products.C4.C4HostControl import C4HostControl
from Products.Mobo.MoboHostControl import MoboHostControl


class HostControlBuilder:
    def __init__(self) -> None:
        self._mainConfigDAO = MainConfigDAO()

    def build_based_on_main_config(self) -> HostControl:
        return self.build(self._mainConfigDAO.get_product())

    def build(self, model: str) -> HostControl:
        if model == "C4":
            return C4HostControl()
        elif model == "MOBO":
            return MoboHostControl()
