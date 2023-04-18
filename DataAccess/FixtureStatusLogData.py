from Core.Enums.FixtureStatus import FixtureStatus
from DataAccess.SqlAlchemyBase import Session
from datetime import datetime, timedelta
from Models.DAO.FixtureStatusLogDAO import FixtureStatusLogDAO
from Models.Fixture import Fixture
import random
import sqlalchemy as db


class FixtureStatusLogData:
    SQL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def add(
        self,
        fixture: Fixture,
        status: FixtureStatus,
        startDateTime: datetime,
        timeDelta: timedelta,
    ):
        endDateTime = startDateTime + timeDelta
        reason = ""
        if status == FixtureStatus.LOCKED:
            reason = fixture.lastLockDescription
        logDAO = FixtureStatusLogDAO(
            fixtureId=fixture.id,
            fixtureIp=fixture.ip,
            status=status.value,
            reason=reason,
            seconds=timeDelta.seconds,
            timeStampStart=startDateTime.isoformat(),
            timeStampEnd=endDateTime.isoformat(),
        )
        session = Session()
        session.add(logDAO)
        session.commit()
        session.close()
        Session.remove()

    def find_last_24H(self, fixtureIp: str):
        now = datetime.now()
        return self.find(fixtureIp, now - timedelta(days=1), now)

    def find(
        self, fixtureIp: str, start: datetime, end: datetime
    ) -> "list[FixtureStatusLogDAO]":
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
                    timeStampEnd BETWEEN '{start.strftime(FixtureStatusLogData.SQL_DATE_FORMAT)}' AND '{end.strftime(FixtureStatusLogData.SQL_DATE_FORMAT)}'
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
                logs.append(FixtureStatusLogDAO(status=record[0], seconds=seconds))
        diffDates = end - start
        unknownSeconds = diffDates.total_seconds() - totalSeconds
        if unknownSeconds > 0:
            logs.append(
                FixtureStatusLogDAO(
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
