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
        return self.find_last(fixtureIp, timedelta(days=1))

    def find_last(
        self, fixtureIp: str, timeDelta: timedelta, groupByMinute: bool = True
    ):
        now = datetime.now()
        return self.find(fixtureIp, now - timeDelta, now, groupByMinute)

    def find(
        self, fixtureIp: str, start: datetime, end: datetime, groupByMinute: bool = True
    ) -> "list[FixtureTempDTO]":
        session = Session()
        temps = []
        try:
            records = session.execute(
                db.text(
                    f"""
                    SELECT
                        ROUND(AVG(temp), 2) as temp,
                        DATE_FORMAT(MAX(timeStamp), '%Y-%c-%d %H:%i:{'00' if groupByMinute else '%S'}') as timeStamp
                    FROM
                        fixture_temp
                    WHERE
                        timeStamp BETWEEN '{start.strftime(FixtureTempDAO.SQL_DATE_FORMAT)}' AND '{end.strftime(FixtureTempDAO.SQL_DATE_FORMAT)}'
                        AND fixtureId = '{fixtureIp}'
                    GROUP BY YEAR(timeStamp), DAY(timeStamp), MONTH(timeStamp), HOUR(timeStamp), MINUTE(timeStamp){'' if groupByMinute else ', SECOND(timeStamp)'};
                    """
                )
            )
            if records != None:
                for record in records:
                    temps.append(
                        FixtureTempDTO(
                            temp=record[0],
                            timeStamp=datetime.strptime(
                                record[1], FixtureTempDAO.SQL_DATE_FORMAT
                            ),
                        )
                    )
        except Exception as e:
            session.rollback()
            print(str(e))
        finally:
            session.close()
            Session.remove()
            return temps
