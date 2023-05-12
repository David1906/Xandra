from DataAccess.SqlAlchemyBase import Base
from sqlalchemy import Column, String, Integer


class SettingDTO(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    text = Column(String(256))
    number = Column(Integer)

    def __init__(self, id: int, name: str = "", text: str = "", number: int = 0):
        self.id = id
        self.name = name
        self.text = text
        self.number = number
