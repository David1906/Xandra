from Core.Enums.SettingType import SettingType
from DataAccess.CatalogItemDAO import CatalogItemDAO
from DataAccess.SettingDAO import SettingDAO
from DataAccess.Strapi.BaseDAO import BaseDAO
from Models.CatalogItem import CatalogItem


class CatalogDAO(BaseDAO):
    def __init__(
        self, settingType: SettingType, settingsDAO: SettingDAO = None
    ) -> None:
        super().__init__(
            settingType,
            settingsDAO,
        )
        self._catalogItemDAO = CatalogItemDAO()

    def find(self):
        results = self._strapiApi.get(f"/{self.group}?pagination[pageSize]=500")
        items = []
        for result in results:
            items.append(result["attributes"]["value"])
        return items

    def _update_items(self):
        items = self.find()

        catalogItems = []
        for item in items:
            catalogItems.append(CatalogItem(self.group, item))

        self._catalogItemDAO.delete_group(self.group)
        self._catalogItemDAO.bulk_add(catalogItems)
