from Core.Enums.FixtureStatus import FixtureStatus
from DataAccess.SqlAlchemyBase import Session
from datetime import datetime, timedelta
from Models.DTO.FixtureStatusLogDTO import FixtureStatusLogDTO
from Models.DTO.FixtureTempDTO import FixtureTempDTO
import random
import sqlalchemy as db


class FixtureTempDAO:
    SQL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def add(
        self,
        fixtureId: int,
        temp: float,
    ):
        tempDTO = FixtureTempDTO(
            fixtureId=fixtureId, temp=temp, timeStamp=datetime.today().isoformat()
        )
        session = Session()
        try:
            session.add(tempDTO)
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
    ) -> "list[FixtureTempDTO]":
        session = Session()
        records = session.execute(
            db.text(
                f"""
                SELECT
                    fixtureId,
                    temp,
                    timeStamp
                FROM 
                    fixture_temp
                WHERE
                    timeStampEnd BETWEEN '{start.strftime(FixtureTempDAO.SQL_DATE_FORMAT)}' AND '{end.strftime(FixtureTempDAO.SQL_DATE_FORMAT)}'
                    AND fixtureId = '{fixtureIp}';"""
            )
        )
        temps = []
        if records != None:
            for record in records:
                temp = float(record[1])
                timestamp = datetime.strptime(record[2], format)
                temps.append(FixtureTempDTO(temp=temp, timestamp=timestamp))
        return temps
