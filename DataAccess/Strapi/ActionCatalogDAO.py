from Core.Enums.SettingType import SettingType
from DataAccess.SettingDAO import SettingDAO
from DataAccess.Strapi.CatalogDAO import CatalogDAO


class ActionCatalogDAO(CatalogDAO):
    def __init__(self, settingsDAO: SettingDAO = None) -> None:
        super().__init__(
            settingType=SettingType.ACTIONS_LAST_SYNC,
            settingsDAO=settingsDAO,
        )
