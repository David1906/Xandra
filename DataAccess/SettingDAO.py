from automapper import mapper
from Core.Enums.SettingType import SettingType
from DataAccess.SqlAlchemyBase import Session
from Models.DTO.SettingDTO import SettingDTO
from Models.Setting import Setting
from sqlalchemy import update


class SettingDAO:
    def add_or_update(self, setting: Setting):
        if self.exists(setting):
            self.update(setting)
        else:
            self.add(setting)

    def exists(self, setting: Setting) -> bool:
        return self.find_DTO(setting.id) != None

    def update(self, setting: Setting):
        dto = self.find_DTO(setting.id)
        if dto == None:
            return
        session = Session()
        try:
            session.execute(
                update(SettingDTO)
                .where(SettingDTO.id == setting.id)
                .values(text=setting.text, number=setting.number)
            )
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def add(self, Setting: Setting):
        session = Session()
        try:
            settingDTO = mapper.to(SettingDTO).map(Setting)
            session.add(settingDTO)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
            Session.remove()

    def find_by_type(self, settingType: SettingType):
        setting = self.find(settingType.value)
        if not self.exists(setting):
            setting.id = settingType.value
            setting.name = settingType.description
        return setting

    def find(self, id: int) -> Setting:
        dto = self.find_DTO_or_default(id)
        return mapper.to(Setting).map(dto)

    def find_DTO_or_default(self, id: int) -> SettingDTO:
        dto = self.find_DTO(id)
        if dto == None:
            dto = SettingDTO(id)
        return dto

    def find_DTO(self, id: int) -> SettingDTO:
        session = Session()
        data = session.query(SettingDTO).where(SettingDTO.id == id).first()
        session.close()
        Session.remove()
        return data
