from DataAccess.EmployeeDAO import EmployeeDAO


class MaintenanceController:
    def __init__(self) -> None:
        self._employeeDAO = EmployeeDAO()

    def exists_employee(self, number: int):
        return self._employeeDAO.exists(number)

    def equals_password(self, number: int, password: str):
        return self._employeeDAO.find(number).equals_password(password)
