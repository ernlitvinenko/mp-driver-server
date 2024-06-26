from random import randint

import sqlalchemy
from firebird.driver import Cursor, Connection
from sqlalchemy import text

from core.model.profile.db import ProfileDB
from .base import BaseStorage


class Storage(BaseStorage):
    def get_profile_by_phone(self, phone_number: str) -> ProfileDB | None:
        stmt = text(f"""
            select SOTR.ID_SOTR, SOTR.SOTR_FULLNAME, phone.PHONE_NUMBER_DGT

            from phone
                left join CONPHONE cros on cros.CONPHONE_ID_PHONE = phone.ID_PHONE
                join SOTR on SOTR.ID_SOTR = cros.CONPHONE_ID_CLICONTACT

            where phone.PHONE_NUMBER_DGT='{phone_number}' and
                  SOTR_DEL = 0 and
                  SOTR_D_UVOL is null and
                  SOTR_SOURCE in (3,4);
        """)
        with self.get_session() as cursor:
            cursor: sqlalchemy.Connection
            data = cursor.execute(stmt).fetchone()

        if not data:
            return None
        return ProfileDB(id=data[0], full_name=data[1], phone_number=data[2])

    def check_profile_code(self, user_id: int, code: int) -> bool:
        stmt = text("""
            select ID_CLIENT_CODES,
       CLIENT_CODES_ID_CLIENT,
       CLIENT_CODES_VALUE from CLIENT_CODES
                          where ID_CLIENT_CODES = (select MAX(ID_CLIENT_CODES)
                           from CLIENT_CODES where CLIENT_CODES_TIP = 5 and CLIENT_CODES_ID_CLIENT = :user_id);
        """)
        with self.get_session() as cursor:
            data = cursor.execute(stmt, {"user_id": user_id}).fetchone()
        if data is not None:
            return data[2] == str(code)

        return False

    def get_profile_by_id(self, profile_id: int):
        stmt = text("""
        
select SOTR.ID_SOTR, SOTR.SOTR_FULLNAME, PHONE.PHONE_NUMBER_DGT from SOTR
                                        left join CONPHONE on CONPHONE.CONPHONE_ID_CLICONTACT = SOTR.ID_SOTR
                                        left join PHONE on CONPHONE.CONPHONE_ID_PHONE = PHONE.ID_PHONE
where SOTR.ID_SOTR = :profile_id;
        """)

        with self.get_session() as cursor:
            data = cursor.execute(stmt, {"profile_id": profile_id}).fetchone()
        if not data:
            return None
        return ProfileDB(id=data[0], full_name=data[1], phone_number=data[2])

    def generate_profile_auth_code(self, user_id: int, phone_dgt: int) -> int:

        code = randint(1000, 9999)

        stmt = text("""
        insert into CLIENT_CODES (client_codes_tip, CLIENT_CODES_VALUE, CLIENT_CODES_ID_CLIENT, CLIENT_CODES_PHONE, CLIENT_CODES_DT)
values (5, :code, :user_id, :phone, localtimestamp);
        """)

        with self.get_session() as session:
            session: sqlalchemy.Connection
            session.execute(stmt, {"code": code, "user_id": user_id, "phone": phone_dgt})
            session.commit()
        return code
