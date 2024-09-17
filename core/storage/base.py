import socket
from contextlib import contextmanager
from typing import ContextManager, NewType, TypeVar, Optional

import sqlalchemy
from firebird.driver import Cursor, Connection
from sqlalchemy import text, Engine

from core.database.db import engine


def row_to_type(self: sqlalchemy.Row):
    return type("KeyedROW", (), {key.upper(): val for key, val in self._mapping.items()})


class _SessionCtxManager:
    def __init__(self, parent: type['BaseStorage']):
        self.parent = parent
        self.con: Optional[sqlalchemy.Connection] = None

    def __enter__(self) -> sqlalchemy.Connection:
        self.con = self.parent.pool.connect()
        if not self.parent.is_authorized(self.con):
            self.parent.db_authorization(self.con)
        return self.con

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()



class BaseStorage:
    pool = engine

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
    def get_session(cls) -> _SessionCtxManager:
        return _SessionCtxManager(parent=cls)

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


sqlalchemy.Row.row_to_type = row_to_type
