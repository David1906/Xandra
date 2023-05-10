from automapper import mapper
from DataAccess.SqlAlchemyBase import Session
from datetime import datetime, timedelta
from Models.DTO.MaintenanceDTO import MaintenanceDTO
from Models.Fixture import Fixture
from Models.Maintenance import Maintenance
from sqlalchemy import update


class MaintenanceDAO:
    SQL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def update(self, maintenance: Maintenance):
        session = Session()
        try:
            maintenanceDTO = (
                session.query(MaintenanceDTO)
                .where(MaintenanceDTO.id == maintenance.id)
                .first()
            )
            if maintenanceDTO == None:
                return
            maintenanceDTO.testId = maintenance.testId
            maintenanceDTO.resultStatus = maintenance.resultStatus
            maintenanceDTO.stepLabel = maintenance.stepLabel
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def add(self, maintenance: Maintenance):
        session = Session()
        try:
            maintenanceDTO = mapper.to(MaintenanceDTO).map(maintenance)
            session.add(maintenanceDTO)
            session.commit()
            maintenance.id = maintenanceDTO.id
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def find(self, fixtureIp: str, start: datetime, end: datetime, qty: int):
        session = Session()
        query = (
            session.query(MaintenanceDTO)
            .filter(MaintenanceDTO.fixtureIp == fixtureIp)
            .filter(
                MaintenanceDTO.dateTime.between(
                    start.strftime(MaintenanceDAO.SQL_DATE_FORMAT),
                    end.strftime(MaintenanceDAO.SQL_DATE_FORMAT),
                )
            )
            .order_by(MaintenanceDTO.dateTime.asc())
            .limit(qty)
        )
        logs: "list[Maintenance]" = []
        for maintenanceDTO in query:
            logs.append(mapper.to(Maintenance).map(maintenanceDTO))
        session.close()
        Session.remove()
        return logs

    def find_not_sync(self) -> "list[Maintenance]":
        session = Session()
        query = (
            session.query(MaintenanceDTO)
            .filter(MaintenanceDTO.isSync != True)
            .filter(MaintenanceDTO.testId > 0)
            .order_by(MaintenanceDTO.id.asc())
        )
        maintenances: "list[Maintenance]" = []
        for maintenanceDTO in query:
            maintenances.append(mapper.to(Maintenance).map(maintenanceDTO))
        session.close()
        Session.remove()
        return maintenances

    def update_is_sync(self, maintenance: Maintenance, isSync: bool):
        session = Session()
        try:
            (
                session.query(MaintenanceDTO)
                .filter(MaintenanceDTO.id == maintenance.id)
                .update({"isSync": isSync})
            )
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def bulk_update_is_sync(
        self, maintenanceDTOs: "list[MaintenanceDTO]", isSync: bool
    ):
        session = Session()
        try:
            items = []
            for maintenanceDTO in maintenanceDTOs:
                items.append({"id": maintenanceDTO.id, "isSync": isSync})

            session.bulk_update_mappings(MaintenanceDTO, items)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()
