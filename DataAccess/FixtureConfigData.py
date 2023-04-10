from automapper import mapper
from DataAccess.FctHostControlData import FctHostControlData
from DataAccess.MainConfigData import MainConfigData
from DataAccess.SqlAlchemyBase import Session
from DataAccess.TestData import TestData
from Models.DAO.FixtureConfigDAO import FixtureConfigDAO
from Models.FixtureConfig import FixtureConfig
from sqlalchemy import update


class FixtureConfigData:
    def __init__(self) -> None:
        self._fctHostControlData = FctHostControlData()
        self._testData = TestData()
        self._mainConfigData = MainConfigData()

    def save(self, fixtureConfigs: "list[FixtureConfig]"):
        for fixtureConfig in fixtureConfigs:
            self.create_or_update(fixtureConfig)

    def create_or_update(self, fixtureConfig: FixtureConfig):
        session = Session()
        fixtureConfigDAO = (
            session.query(FixtureConfigDAO)
            .where(FixtureConfigDAO.ip == fixtureConfig.ip)
            .first()
        )
        if fixtureConfigDAO == None:
            fixtureConfigDAO = mapper.to(FixtureConfigDAO).map(fixtureConfig)
            fixtureConfigDAO.isDisabled = fixtureConfig.is_disabled()
            session.add(fixtureConfigDAO)
        else:
            session.execute(
                update(FixtureConfigDAO)
                .where(FixtureConfigDAO.ip == fixtureConfig.ip)
                .values(
                    ip=fixtureConfig.ip,
                    isDisabled=fixtureConfig.is_disabled(),
                    isSkipped=fixtureConfig.isSkipped,
                    isRetestMode=fixtureConfig.isRetestMode,
                    enableLock=fixtureConfig.enableLock,
                )
            )
        session.commit()
        Session.remove()

    def is_skipped(self, fixtureIp: str) -> bool:
        fixtureConfigDAO = self.find_DAO(fixtureIp)
        if fixtureConfigDAO == None:
            return False
        else:
            return fixtureConfigDAO.isSkipped

    def is_retest_mode(self, fixtureIp: str) -> bool:
        fixtureConfigDAO = self.find_DAO(fixtureIp)
        if fixtureConfigDAO == None:
            return False
        else:
            return fixtureConfigDAO.isRetestMode

    def is_lock_enabled(self, fixtureIp: str) -> bool:
        fixtureConfigDAO = self.find_DAO(fixtureIp)
        if fixtureConfigDAO == None:
            return True
        else:
            return fixtureConfigDAO.enableLock

    def find_DAO(self, fixtureIp: str) -> FixtureConfigDAO:
        session = Session()
        data = (
            session.query(FixtureConfigDAO)
            .where(FixtureConfigDAO.ip == fixtureIp)
            .first()
        )
        session.close()
        Session.remove()
        return data

    def find(self, fixtureIp: str) -> FixtureConfig:
        for fixture in self._fctHostControlData.get_all_fixture_configs():
            if fixtureIp == fixture[FctHostControlData.PLC_IP_KEY]:
                return FixtureConfig(
                    fixture[FctHostControlData.PLC_ID_KEY],
                    fixtureIp,
                    self._testData.get_yield(fixtureIp),
                    self._testData.are_last_test_pass(fixtureIp),
                    self.is_skipped(fixtureIp),
                    self._mainConfigData.get_yield_error_threshold(),
                    self._mainConfigData.get_yield_warning_threshold(),
                    isRetestMode=self.is_retest_mode(fixtureIp),
                    areLastTestFail=self._testData.are_last_test_fail(fixtureIp),
                    enableLock=self.is_lock_enabled(fixtureIp),
                    lockFailQty=self._mainConfigData.get_lock_fail_qty(),
                )
