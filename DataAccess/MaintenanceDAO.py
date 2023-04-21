from automapper import mapper
from DataAccess.SqlAlchemyBase import Session
from Models.DTO.MaintenanceDTO import MaintenanceDTO
from Models.Fixture import Fixture
from Models.Maintenance import Maintenance
from datetime import datetime, timedelta


class MaintenanceDAO:
    SQL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def update(self, maintenance: Maintenance):
        session = Session()
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
        Session.remove()

    def add(self, maintenance: Maintenance):
        session = Session()
        maintenanceDTO = mapper.to(MaintenanceDTO).map(maintenance)
        session.add(maintenanceDTO)
        session.commit()
        maintenance.id = maintenanceDTO.id
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
            .filter(MaintenanceDTO.isSync == False)
            .filter( MaintenanceDTO.testId > 0)
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
        (
            session.query(MaintenanceDTO)
            .filter(MaintenanceDTO.id == maintenance.id)
            .update({"isSync": isSync})
        )
        session.commit()
        session.close()
        Session.remove()
