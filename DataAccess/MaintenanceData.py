from automapper import mapper
from DataAccess.SqlAlchemyBase import Session
from Models.DAO.MaintenanceDAO import MaintenanceDAO
from Models.Fixture import Fixture
from Models.Maintenance import Maintenance
from datetime import datetime, timedelta


class MaintenanceData:
    SQL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def update(self, maintenance: Maintenance):
        session = Session()
        maintenanceDAO = (
            session.query(MaintenanceDAO)
            .where(MaintenanceDAO.id == maintenance.id)
            .first()
        )
        if maintenanceDAO == None:
            return
        maintenanceDAO.testId = maintenance.testId
        maintenanceDAO.resultStatus = maintenance.resultStatus
        maintenanceDAO.stepLabel = maintenance.stepLabel
        session.commit()
        Session.remove()

    def add(self, maintenance: Maintenance):
        session = Session()
        maintenanceDAO = mapper.to(MaintenanceDAO).map(maintenance)
        session.add(maintenanceDAO)
        session.commit()
        maintenance.id = maintenanceDAO.id
        Session.remove()

    def find(self, fixtureIp: str, start: datetime, end: datetime, qty: int):
        session = Session()
        query = (
            session.query(MaintenanceDAO)
            .filter(MaintenanceDAO.fixtureIp == fixtureIp)
            .filter(
                MaintenanceDAO.dateTime.between(
                    start.strftime(MaintenanceData.SQL_DATE_FORMAT),
                    end.strftime(MaintenanceData.SQL_DATE_FORMAT),
                )
            )
            .order_by(MaintenanceDAO.dateTime.asc())
            .limit(qty)
        )
        logs: "list[Maintenance]" = []
        for maintenanceDAO in query:
            logs.append(mapper.to(Maintenance).map(maintenanceDAO))
        session.close()
        Session.remove()
        return logs
