from DataAccess.SqlAlchemyBase import Base
from sqlalchemy import Column, String, Integer


class CatalogItemDTO(Base):
    __tablename__ = "catalog_items"

    id = Column(Integer, primary_key=True)
    group = Column(String(256))
    value = Column(String(256))

    def __init__(self, group: str, value: str = ""):
        self.group = group
        self.value = value
