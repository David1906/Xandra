from Core.Enums.SettingType import SettingType
from DataAccess.SettingDAO import SettingDAO
from DataAccess.Strapi.BaseDAO import BaseDAO
from DataAccess.EmployeeDAO import EmployeeDAO as DBEmployeeDAO
from Models.Employee import Employee


class EmployeeDAO(BaseDAO):
    def __init__(self, settingsDAO: SettingDAO = None) -> None:
        super().__init__(
            settingType=SettingType.EMPLOYEES_LAST_SYNC,
            settingsDAO=settingsDAO,
        )
        self._dbEmployeeDAO = DBEmployeeDAO()

    def find(self) -> "list[Employee]":
        results = self._strapiApi.get(f"/{self.group}?pagination[pageSize]=500")
        items = []
        for result in results:
            try:
                items.append(
                    Employee(
                        number=int(result["attributes"]["number"]),
                        name=str(result["attributes"]["name"]),
                        password=str(result["attributes"]["password"]),
                    )
                )
            except:
                pass
        return items

    def _update_items(self):
        employees = self.find()
        self._dbEmployeeDAO.truncate()
        self._dbEmployeeDAO.bulk_add(employees)
