import socket
from contextlib import contextmanager
from typing import ContextManager

import sqlalchemy
from firebird.driver import Cursor, Connection
from sqlalchemy import text

from core.database.db import engine


class BaseStorage:
    _pool = engine

    @staticmethod
    def db_authorization(con: sqlalchemy.Connection):
        stmt = text(f"""
     UPDATE SEANS 
set SEANS_STATUS    = 2,
            SEANS_ID_SOTR   = 31,--14,
            SEANS_ID_MST    = 0,  -- без привязки
            SEANS_COMP_NAME = '{socket.gethostname()}',--//'PersonalArea'
            SEANS_REMOTE_VER = '2024052901'
where ID_SEANS = RDB$GET_CONTEXT('USER_SESSION', 'ID_SEANS');   
        """)

        con.execute(stmt)
        con.commit()

    @staticmethod
    def is_authorized(con: sqlalchemy.Connection):
        stmt = text("""
            select SEANS_ID_SOTR from SEANS where ID_SEANS = RDB$GET_CONTEXT('USER_SESSION', 'ID_SEANS')
        """)
        return con.execute(stmt).fetchone()[0] == 31

    @classmethod
    @contextmanager
    def get_session(cls) -> ContextManager[sqlalchemy.Connection]:
        connection = cls._pool.connect()
        if not cls.is_authorized(connection):
            cls.db_authorization(connection)

        try:
            yield connection
        finally:
            connection.close()

    # @classmethod
    # @contextmanager
    # def get_cursor(cls) -> ContextManager[]:
    #     with cls.get_session() as session:
    #         session: sqlalchemy.Connection
    #         cursor = session.cursor()
    #         try:
    #             yield cursor
    #         finally:
    #             cursor.close()
