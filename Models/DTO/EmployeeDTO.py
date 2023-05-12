from DataAccess.SqlAlchemyBase import Base
from sqlalchemy import Column, String, Integer


class EmployeeDTO(Base):
    __tablename__ = "employees"

    number = Column(Integer, primary_key=True)
    name = Column(String(256))
    encryptedPassword = Column(String(256))

    def __init__(self, number: int = 0, name: str = "", encryptedPassword: str = ""):
        self.number = number
        self.name = name
        self.encryptedPassword = encryptedPassword
