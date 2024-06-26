import functools
import json
from datetime import date, datetime
from typing import Self, Optional, Union, Any, Callable

from firebird.driver import Cursor
from pydantic import BaseModel, Field, Json
from pypika import Query, Table
from pypika.queries import QueryBuilder

from core.database.db import redis_cache_obj
from core.storage.base import BaseStorage

from redis_cache import RedisCache


class __BaseDB(BaseModel, BaseStorage):
    __tablename__: str
    __read_only: bool = False
    __table: Table | None = None
    __state_changed = {}
    __query: QueryBuilder | None = None

    @classmethod
    def cache(cls) -> RedisCache:
        return redis_cache_obj()

    @classmethod
    def get_keys(cls):
        return [x for x in cls.__dict__['__annotations__'].keys() if not x.startswith("__")]

    @classmethod
    def get_table(cls) -> Self:
        return Table(cls.__tablename__)

    @classmethod
    def fetch_one(cls, id: int) -> type[Self]:
        t = cls.get_table()
        keys = cls.get_keys()
        stmt = Query.from_(t).select(*keys).where(getattr(t, keys[0]) == id)
        with cls.get_cursor() as cur:
            cur: Cursor
            data = cur.execute(stmt.get_sql()).fetchone()

        return cls(**{key: val for key, val in zip(keys, data)})

    @classmethod
    def parse_orm(cls, row):
        return cls(**{key: val for key, val in zip(cls.get_keys(), row)})

    @classmethod
    def fetch_all(cls, where_query: QueryBuilder = None) -> list['Self']:
        table = cls.get_table()
        if not where_query:
            stmt = Query.from_(table).select(*cls.get_keys())
        else:
            stmt = Query.from_(table).select(*cls.get_keys()).where(where_query)

        with cls.get_cursor() as cursor:
            cursor: Cursor
            stmt: QueryBuilder
            print(stmt)
            data = cursor.execute(stmt.get_sql()).fetchall()
        return [cls.parse_orm(d) for d in data]

    @classmethod
    def fetch_related(cls) -> 'Self':
        table = cls.get_table()

        cls.__query = Query.from_(table)
        return cls

    @classmethod
    def create(cls, model: Self) -> Self:
        if model.__read_only:
            raise Exception("This model is read only")

        # table = self.get_table()

        # data = self.model_dump(mode='json', exclude_none=True, exclude={'id'}, exclude_unset=True)
        # stmt = Query.into(table).columns(*[self.get_keys()]).insert(
        #     *[kwargs[key] for key in self.get_keys() if key in kwargs.keys()])
        # with self.get_cursor() as cursor:
        #     cursor: Cursor
        # cursor.execute(stmt.get_sql())

    @classmethod
    def update(cls, model: Self) -> Self:
        if model.__read_only:
            raise Exception("This model is read only")


class MPLSTDB(__BaseDB):
    __tablename__: str = "LST"
    ID_LST: int
    LST_ID_VLST: int
    LST_NAME: str
    LST_NAME_SH: str

    @classmethod
    def fetch_one(cls, id: int) -> type[Self]:
        cache = cls.cache()

        @cache.cache()
        def wrapper(id):
            return super(MPLSTDB, cls).fetch_one(id)

        return wrapper(id)


class MPAppTaskDB(__BaseDB):
    __tablename__: str = "APP_TASK"
    ID_APP_TASK: int | None = None
    APP_TASK_ID_SOTR: int = None
    APP_TASK_ID_APP_TASK: int = None
    APP_TASK_DT_START_PLN: datetime = None
    APP_TASK_DT_END_PLN: datetime = None
    APP_TASK_DT_START_FACT: datetime | None = None
    APP_TASK_DT_END_FACT: datetime | None = None
    APP_TASK_STATUS: int = None
    APP_TASK_TIP: int = None
    APP_TASK_TEXT: str = None
    APP_TASK_DEL: int = None

    @property
    def status(self) -> MPLSTDB:
        return MPLSTDB.fetch_one(self.APP_TASK_STATUS)

    @property
    def is_subtask(self) -> bool:
        return self.ID_APP_TASK != self.APP_TASK_ID_APP_TASK

    @property
    def task_type(self) -> MPLSTDB:
        return MPLSTDB.fetch_one(self.APP_TASK_TIP)

    @property
    def subtasks(self) -> list['MPAppTaskDB']:
        t: MPAppTaskDB = MPAppTaskDB.get_table()
        return MPAppTaskDB.fetch_all(
            (t.APP_TASK_ID_APP_TASK == self.ID_APP_TASK) & (t.APP_TASK_ID_APP_TASK != t.ID_APP_TASK) & (
                    t.APP_TASK_DEL == 0))

    @property
    def events(self) -> list['MPAppEventDB']:
        return MPAppEventDB.fetch_all(MPAppEventDB.get_table().APP_EVENT_ID_REC == self.ID_APP_TASK)

    @property
    def params(self) -> list['MPAppParamDB']:
        return MPAppParamDB.fetch_all(MPAppParamDB.get_table().APP_PARAM_ID_REC == self.ID_APP_TASK)


class EventData(__BaseDB):
    key: MPLSTDB
    value: Any


class MPAppEventDB(__BaseDB):
    __tablename__: str = "APP_EVENT"
    ID_APP_EVENT: int = None
    APP_EVENT_ID_SOTR: int = None
    APP_EVENT_ID_REC: int = None
    APP_EVENT_VID: int = None
    APP_EVENT_TIP: int = None
    APP_EVENT_DT: datetime | None = None
    APP_EVENT_TEXT: str | None = None
    APP_EVENT_DATA: Json
    APP_EVENT_DEL: int = 0

    @property
    def event_type(self) -> MPLSTDB:
        return MPLSTDB.fetch_one(self.APP_EVENT_TIP)

    @property
    def event_data(self) -> list[EventData]:
        return [EventData(key=MPLSTDB.fetch_one(key), value=value) for d in list(self.APP_EVENT_DATA) for key, value in
                d.items()]


class MPMSTDB(__BaseDB):
    __read_only = True
    __tablename__ = "MST"
    ID_MST: int = Field(default=0)
    MST_PR_OTHER: int = Field(default=0)
    MST_ID_KG: int = Field(default=0)
    MST_ID_SRV: int = Field(default=0)
    MST_ID_SETTLEMENT: Optional[int] = Field(default=0)
    MST_SID: Optional[str] = Field(default=None)
    MST_NAME: Optional[str] = Field(default=None)
    MST_CLI_NAME: Optional[str] = Field(default=None)
    MST_CODE: int = Field(default=0)
    MST_CODE_PODR_NDS: int | None = Field(default=0)
    MST_CODE_PODR_BN: int | None = Field(default=0)
    MST_PR_TTNINPUT: int = Field(default=0)
    MST_PR_TTNOUTPUT: int = Field(default=0)
    MST_PR_AEX: int = Field(default=0)
    MST_PR_AEX_ADR: Optional[int] = Field(default=0)
    MST_ID_MST_TTNOUTPUT: int = Field(default=0)
    MST_PR_SORT: int = Field(default=0)
    MST_PR_PVZ: int = Field(default=0)
    MST_PR_VIRT: int = Field(default=0)
    MST_PR_INOTHER: int = Field(default=0)
    MST_PR_ZAKG: int = Field(default=0)
    MST_PR_FAR: int = Field(default=0)
    MST_PR_KKT: int = Field(default=0)
    MST_PR_CC: int = Field(default=0)
    MST_PR_AS: int = Field(default=0)
    MST_KM: int = Field(default=0)
    MST_MP: int = Field(default=0)
    MST_ID_AGENT_AS: int = Field(default=0)
    MST_PR_NOLIM_AS: int = Field(default=0)
    MST_PR_WC_AS: int = Field(default=0)
    MST_PR_TRS: int = Field(default=0)
    MST_ID_REGION: int = Field(default=0)
    MST_ADDRESS_CODE: int = Field(default=0)
    MST_ID_KLADR_DOM: Optional[int] = Field(default=0)
    MST_SHIR: float = Field(default=0.0)
    MST_DOLG: float = Field(default=0.0)
    MST_ADR_STOR: Optional[str] = Field(default=None)
    MST_FUNC_MASK: int = Field(default=0)
    MST_ID_SRV_CALL: int = Field(default=0)
    MST_ID_MST_CALL: int = Field(default=0)
    MST_PR_DIRECT: int = Field(default=0)
    MST_NAME_DIRECT: Optional[str] = Field(default=None)
    MST_PR_NOTE: int = Field(default=0)
    MST_PR_NOTSITE: int = Field(default=0)
    MST_PR_GREEN: int = Field(default=0)
    MST_PR_GREENORK: int = Field(default=0)
    MST_PR_GREENPRINTER: int = Field(default=0)
    MST_PR_VID_TR_VD: int = Field(default=0)
    MST_PR_BAN_IN: int = Field(default=0)
    MST_PR_NO_CLIENT_CODES: int = Field(default=0)
    MST_PR_NO_STTN02: int = Field(default=0)
    MST_PR_NO_EEU: int = Field(default=0)
    MST_VID_CALC_FOBYOM: int = Field(default=0)
    MST_TXT: Optional[str] = Field(default=None)
    MST_DEL: int = Field(default=0)
    MST_CH: Optional[datetime] = Field(default=None)
    MST_WCH: int = Field(default=0)
    MST_IMP: Optional[datetime] = Field(default=None)
    MST_MPOST: int = Field(default=0)
    MST_SEANS: int = Field(default=0)
    MST_OWNERMST: int = Field(default=0)
    MST_CR: Optional[datetime] = Field(default=None)
    MST_WCR: int = Field(default=0)
    MST_FIMP: Optional[datetime] = Field(default=None)
    MST_ID_MST_SYNONYM: int = Field(default=0)
    MST_NAME_OLD: Optional[str] = Field(default=None)
    MST_SRC_OLD: int = Field(default=0)
    MST_UPPERNAME_OLD: Optional[str] = Field(default=None)
    MST_TXT_AEX: Optional[str] = Field(default=None)
    MST_PR_NODOOR_AEX: int = Field(default=0)

    @classmethod
    def fetch_one(cls, id: int) -> type[Self]:
        cache = cls.cache()

        @cache.cache()
        def wrapper(id):
            return super(MPMSTDB, cls).fetch_one(id)

        return wrapper(id)


class MPTRSDB(__BaseDB):
    __tablename__ = "TRS"
    __read_only = True
    ID_TRS: int = Field(default=0)
    TRS_PR_TEST: int = Field(default=0)
    TRS_PR_TEST_ID_SOTR: int = Field(default=0)
    TRS_PR_TEST_DT: Optional[datetime] = Field(default=None)
    TRS_PR: int = Field(default=0)
    TRS_PR_UP: int = Field(default=0)
    TRS_ID_LST_PR: int = Field(default=0)
    TRS_ID_LST_VID: int = Field(default=0)
    TRS_ID_LSTU_TIP: int = Field(default=0)
    TRS_SID: Optional[str] = Field(default=None)
    TRS_SID_GOST: Optional[str] = Field(default=None)
    TRS_SID_OLD: Optional[str] = Field(default=None)
    TRS_SRC_OLD: int = Field(default=0)
    TRS_PR_VLAD: int = Field(default=0)
    TRS_ID_AGENT_AS: int = Field(default=0)
    TRS_VES: float = Field(default=0.0)
    TRS_OBYOM: float = Field(default=0.0)
    TRS_PR_LTOR: int = Field(default=0)
    TRS_PR_LLEN: int = Field(default=0)
    TRS_PR_LTOP: int = Field(default=0)
    TRS_PR_TEPL: int = Field(default=0)
    TRS_PR_TEPL_WHERE: int = Field(default=0)
    TRS_OBYOM_TEPL: float = Field(default=0.0)
    TRS_PR_NOZAGRGRUZ: int = Field(default=0)
    TRS_CNT_AXIS: int = Field(default=0)
    TRS_PRIM: Optional[str] = Field(default=None)
    TRS_INFO: Optional[str] = Field(default=None)
    TRS_TARA: Optional[float] = Field(default=0.0)
    TRS_TYPEPROPERTY: int = Field(default=0)
    TRS_DOGAREND: Optional[str] = Field(default=None)
    TRS_1C_D_AKT: Optional[date] = Field(default=None)
    TRS_1C_NOMMSG: int = Field(default=0)
    TRS_1C_DEL: int = Field(default=0)
    TRS_1C_DATEEND: Optional[date] = Field(default=None)
    TRS_DEL: int = Field(default=0)
    TRS_CR: Optional[datetime] = Field(default=None)
    TRS_WCR: int = Field(default=0)
    TRS_CH: Optional[datetime] = Field(default=None)
    TRS_WCH: int = Field(default=0)
    TRS_OWNERMST: int = Field(default=0)
    TRS_SEANS: int = Field(default=0)
    TRS_IMP: Optional[datetime] = Field(default=None)
    TRS_FIMP: Optional[datetime] = Field(default=None)
    TRS_MPOST: int = Field(default=0)

    @classmethod
    def fetch_one(cls, id: int) -> type[Self]:
        cache = cls.cache()

        @cache.cache()
        def wrapper(id):
            return super(MPTRSDB, cls).fetch_one(id)

        return wrapper(id)


class MPMarshDB(__BaseDB):
    __read_only = True
    __tablename__ = "MARSH"
    ID_MARSH: int = Field(default=0)
    MARSH_PR: int = Field(default=0)
    MARSH_PR_PLAN: int = Field(default=0)
    MARSH_PR_VLAD: int = Field(default=0)
    MARSH_PR_DOP: int = Field(default=0)
    MARSH_PR_TEPL: int = Field(default=0)
    MARSH_KEY_GPREF: Optional[str] = Field(default=None, min_length=1, max_length=16)
    MARSH_KEY_PREF: Optional[str] = Field(default=None, min_length=1, max_length=32)
    MARSH_NAME: Optional[str] = Field(default=None, min_length=1, max_length=128)
    MARSH_D_N: Optional[date] = Field(default=None)
    MARSH_D_K: Optional[date] = Field(default=None)
    MARSH_ID_MST_OTPR: int = Field(default=0)
    MARSH_ID_MST_NAZN: int = Field(default=0)
    MARSH_DAYS_WEEK: int = Field(default=0)
    MARSH_T_OTPR: float = Field(default=0.0)
    MARSH_DATE_OUT: Optional[date] = Field(default=None)
    MARSH_PRICE: Optional[float] = Field(default=0.0)
    MARSH_KM: Optional[float] = Field(default=0.0)
    MARSH_TXT: Optional[str] = Field(default=None, min_length=1, max_length=512)
    MARSH_DEL: int = Field(default=0)


class MPMarshTRSDB(__BaseDB):
    __tablename__ = "MARSH_TRS"
    __read_only = True
    ID_MARSH_TRS: int = Field(default=0)
    MARSH_TRS_ID_MARSH: int = Field(default=0)
    MARSH_TRS_DATE: Optional[date] = Field(default=None)
    MARSH_TRS_ID_TRS: int = Field(default=0)
    MARSH_TRS_TRS_PR_COLDONLY: Optional[int] = Field(default=0)
    MARSH_TRS_ID_PRIC: int = Field(default=0)
    MARSH_TRS_PRIC_PR_COLDONLY: Optional[int] = Field(default=0)
    MARSH_TRS_ID_SOTR: int = Field(default=0)
    MARSH_TRS_DT_DELIVERY: Optional[datetime] = Field(default=None)
    MARSH_TRS_PR: int = Field(default=0)
    MARSH_TRS_COMMENT: Optional[str] = Field(default=None, max_length=4096)
    MARSH_TRS_TARIFF: float = Field(default=0.0)
    MARSH_TRS_DEL: int = Field(default=0)
    MARSH_TRS_OWNERMST: int = Field(default=0)
    MARSH_TRS_MPOST: Optional[int] = Field(default=0)
    MARSH_TRS_CR: Optional[datetime] = Field(default=None)
    MARSH_TRS_WCR: int = Field(default=0)
    MARSH_TRS_IMP: Optional[datetime] = Field(default=None)
    MARSH_TRS_CH: Optional[datetime] = Field(default=None)
    MARSH_TRS_WCH: int = Field(default=0)
    MARSH_TRS_SEANS: int = Field(default=0)
    MARSH_TRS_FIMP: Optional[datetime] = Field(default=None)

    @property
    def marsh(self) -> MPMarshDB:
        return MPMarshDB.fetch_one(self.MARSH_TRS_ID_MARSH)

    @property
    def trs(self) -> MPTRSDB:
        return MPTRSDB.fetch_one(self.MARSH_TRS_ID_TRS)

    @property
    def trailer(self) -> MPTRSDB:
        return MPTRSDB.fetch_one(self.MARSH_TRS_ID_PRIC)


class MPAppParamDB(__BaseDB):
    __tablename__ = "APP_PARAM"
    __read_only = True
    APP_PARAM_ID_REC: int = Field(default=0)
    APP_PARAM_STR: Optional[str] = Field(default=None, min_length=1, max_length=1024)
    APP_PARAM_VID: int = Field(default=0)
    APP_PARAM_TIP: int = Field(default=0)
    APP_PARAM_DEL: int = Field(default=0)
    APP_PARAM_CR: Optional[datetime] = Field(default=None)
    APP_PARAM_WCR: int = Field(default=0)
    APP_PARAM_CH: Optional[datetime] = Field(default=None)
    APP_PARAM_WCH: int = Field(default=0)

    @property
    def param_type(self) -> MPLSTDB:
        return MPLSTDB.fetch_one(self.APP_PARAM_TIP)

    @property
    def related_table(self) -> Union['MPMSTDB', 'MPMarshTRSDB', 'MPTRSDB', 'MPMarshDB']:
        query = {
            "ID_MARSH_TRS": MPMarshTRSDB,
            "ID_MST": MPMSTDB,
            "ID_TRS": MPTRSDB,
            "ID_MARSH": MPMarshDB
        }
        return query[self.param_type.LST_NAME_SH].fetch_one(self.APP_PARAM_STR)

