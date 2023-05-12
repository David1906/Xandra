from automapper import mapper
from DataAccess.SqlAlchemyBase import Session
from sqlalchemy.sql import text as sa_text
from Models.DTO.EmployeeDTO import EmployeeDTO
from Models.Employee import Employee


class EmployeeDAO:
    def bulk_add(self, employees: "list[Employee]"):
        session = Session()
        try:
            items = []
            for employee in employees:
                items.append(
                    {
                        "number": employee.number,
                        "name": employee.name,
                        "encryptedPassword": employee.encryptedPassword,
                    }
                )
            session.bulk_insert_mappings(EmployeeDTO, items)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def add(self, employee: Employee):
        session = Session()
        try:
            employeeDTO = mapper.to(EmployeeDTO).map(employee)
            session.add(employeeDTO)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def find(self, number: int) -> Employee:
        dao = self.find_DTO_or_default(number)
        return mapper.to(Employee).map(dao)

    def find_DTO_or_default(self, number: int) -> EmployeeDTO:
        dto = self.find_DTO(number)
        if dto == None:
            dto = EmployeeDTO()
        return dto

    def exists(self, number: int):
        return self.find_DTO(number) != None

    def find_DTO(self, number: int) -> EmployeeDTO:
        session = Session()
        data = session.query(EmployeeDTO).where(EmployeeDTO.number == number).first()
        session.close()
        Session.remove()
        return data

    def truncate(self):
        session = Session()
        try:
            session.execute(sa_text(f"""TRUNCATE TABLE {EmployeeDTO.__tablename__}"""))
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()
