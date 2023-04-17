from Core.Enums.FixtureStatus import FixtureStatus
from DataAccess.SqlAlchemyBase import Session
from Models.DAO.FixtureStatusLogDAO import FixtureStatusLogDAO
from Models.Fixture import Fixture
from datetime import datetime, timedelta


class FixtureStatusLogData:
    def add(self, fixture: Fixture, status: FixtureStatus, timeDelta: timedelta):
        now = datetime.now()
        startTime = now - timeDelta
        reason = ""
        if status == FixtureStatus.LOCKED:
            reason = fixture.lastLockDescription
        logDAO = FixtureStatusLogDAO(
            fixtureId=fixture.id,
            fixtureIp=fixture.ip,
            status=status.value,
            reason=reason,
            seconds=timeDelta.seconds,
            timeStampStart=startTime.isoformat(),
            timeStampEnd=now.isoformat(),
        )
        session = Session()
        session.add(logDAO)
        session.commit()
        session.close()
        Session.remove()
