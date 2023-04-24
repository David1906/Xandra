from Core.Enums.FixtureStatus import FixtureStatus
from DataAccess.SqlAlchemyBase import Session
from datetime import datetime, timedelta
from Models.DTO.FixtureStatusLogDTO import FixtureStatusLogDTO
from Models.Fixture import Fixture
import random
import sqlalchemy as db


class FixtureStatusLogDAO:
    SQL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def add(
        self,
        fixture: Fixture,
        status: FixtureStatus,
        startDateTime: datetime,
        timeDelta: timedelta,
    ):
        if timeDelta.total_seconds() <= 0:
            return
        endDateTime = startDateTime + timeDelta
        reason = ""
        if status == FixtureStatus.LOCKED:
            reason = fixture.lastLockDescription
        logDTO = FixtureStatusLogDTO(
            fixtureId=fixture.id,
            fixtureIp=fixture.ip,
            status=status.value,
            reason=reason,
            seconds=timeDelta.seconds,
            timeStampStart=startDateTime.isoformat(),
            timeStampEnd=endDateTime.isoformat(),
        )
        session = Session()
        try:
            session.add(logDTO)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def find_last_24H(self, fixtureIp: str):
        now = datetime.now()
        return self.find(fixtureIp, now - timedelta(days=1), now)

    def find(
        self, fixtureIp: str, start: datetime, end: datetime
    ) -> "list[FixtureStatusLogDTO]":
        session = Session()
        records = session.execute(
            db.text(
                f"""
                SELECT
                    status,
                    SUM(seconds) as seconds
                FROM 
                    fixture_status_logs
                WHERE
                    timeStampEnd BETWEEN '{start.strftime(FixtureStatusLogDAO.SQL_DATE_FORMAT)}' AND '{end.strftime(FixtureStatusLogDAO.SQL_DATE_FORMAT)}'
                    AND fixtureIp = '{fixtureIp}'
                GROUP BY status;"""
            )
        )
        logs = []
        totalSeconds = 0
        if records != None:
            for record in records:
                seconds = int(record[1])
                totalSeconds += seconds
                logs.append(FixtureStatusLogDTO(status=record[0], seconds=seconds))
        diffDates = end - start
        unknownSeconds = diffDates.total_seconds() - totalSeconds
        if unknownSeconds > 0:
            logs.append(
                FixtureStatusLogDTO(
                    status=FixtureStatus.UNKNOWN.value, seconds=unknownSeconds
                )
            )
        return logs

    def seed_logs(self):
        fixture = Fixture(
            id=1,
            ip="192.167.1.119",
            yieldErrorThreshold=0,
            yieldWarningThreshold=70,
            lockFailQty=3,
            unlockPassQty=1,
        )
        accumDate = datetime(2023, 4, 17)
        endDate = datetime(2023, 4, 19)
        while accumDate <= endDate:
            status = FixtureStatus(random.randint(1, 3))
            timeDelta = timedelta(seconds=random.randint(1, 5400))
            self.add(fixture, status, accumDate, timeDelta)
            accumDate += timeDelta

    def find_not_sync(self) -> "list[FixtureStatusLogDTO]":
        session = Session()
        query = (
            session.query(FixtureStatusLogDTO)
            .filter(FixtureStatusLogDTO.isSync == False)
            .order_by(FixtureStatusLogDTO.id.asc())
        )
        logs: "list[FixtureStatusLogDTO]" = []
        for fixtureStatusLogDTO in query:
            logs.append(fixtureStatusLogDTO)
        session.close()
        Session.remove()
        return logs

    def update_is_sync(self, fixtureStatusLogDTO: FixtureStatusLogDTO, isSync: bool):
        session = Session()
        try:
            (
                session.query(FixtureStatusLogDTO)
                .filter(FixtureStatusLogDTO.id == fixtureStatusLogDTO.id)
                .update({"isSync": isSync})
            )
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()
