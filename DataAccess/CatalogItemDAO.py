from automapper import mapper
from DataAccess.SqlAlchemyBase import Session
from Models.DTO.CatalogItemDTO import CatalogItemDTO
from sqlalchemy.sql import text as sa_text
from Models.CatalogItem import CatalogItem
from sqlalchemy import update


class CatalogItemDAO:
    def bulk_add(self, catalogItems: "list[CatalogItem]"):
        session = Session()
        try:
            items = []
            for catalogItem in catalogItems:
                items.append(
                    {
                        "group": catalogItem.group,
                        "value": catalogItem.value,
                    }
                )
            session.bulk_insert_mappings(CatalogItemDTO, items)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def find_group_values(self, group: str) -> "list[str]":
        return [catalogItem.value for catalogItem in self.find_group(group)]

    def find_group(self, group: str) -> "list[CatalogItem]":
        session = Session()
        daos = session.query(CatalogItemDTO).where(CatalogItemDTO.group == group).all()
        session.close()
        Session.remove()
        items = [CatalogItem(group, "")]
        items.extend([mapper.to(CatalogItem).map(dao) for dao in daos])
        return items

    def truncate(self):
        session = Session()
        try:
            session.execute(
                sa_text(f"""TRUNCATE TABLE {CatalogItemDTO.__tablename__}""")
            )
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()
