from Core.Enums.SettingType import SettingType
from DataAccess.MainConfigDAO import MainConfigDAO
from DataAccess.SettingDAO import SettingDAO
from DataAccess.Strapi.StrapiApi import StrapiApi
from Utils.Translator import Translator

_ = Translator().gettext


class BaseDAO:
    def __init__(
        self, settingType: SettingType, settingsDAO: SettingDAO = None
    ) -> None:
        self._settingType = settingType
        self._settingsDAO = SettingDAO() if settingsDAO == None else settingsDAO
        self._strapiApi = StrapiApi(url=MainConfigDAO().get_sync_server())

    def should_sync(self) -> bool:
        lastSync = self._settingsDAO.find_by_type(self._settingType)
        lastDBUpdate = self.find_last_db_update()
        return lastDBUpdate != None and lastSync.text != lastDBUpdate

    def sync(self) -> bool:
        self._update_items()
        self._update_last_sync()

    def _update_items(self):
        pass

    def _update_last_sync(self):
        setting = self._settingsDAO.find_by_type(self._settingType)
        setting.text = self.find_last_db_update()
        self._settingsDAO.add_or_update(setting)

    def find_last_db_update(self) -> str:
        try:
            result = self._strapiApi.get(f"/{self.group[:-1]}/lastUpdate")
            return result["updateTime"]
        except:
            raise Exception("Api no response")

    def find(self):
        pass

    @property
    def group(self) -> str:
        return self._settingType.group
