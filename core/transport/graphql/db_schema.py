from dataclasses import dataclass
from typing import Optional, TypeVar, Any, NewType, TypedDict

import strawberry
from sqlalchemy import text, CursorResult, Sequence, Row, TextClause

from core.storage import base_storage

T = TypeVar("T")


@dataclass
class EXEC_STATEMENT:
    rows: CursorResult
    data: list[Any]


def return_strawberry_model(model: type[T], rows: CursorResult, data: Sequence[Row]) -> list[T]:
    return [model(**{rows._metadata.keys._keys[idx].upper(): elem for idx, elem in enumerate(row) if
                     rows._metadata.keys._keys[idx].upper() in model.__annotations__}) for row in data]


def exec_statement(stmt: TextClause, **kwargs) -> EXEC_STATEMENT:
    with base_storage.get_session() as session:
        rows = session.execute(stmt, kwargs)
        data = rows.fetchall()
    return EXEC_STATEMENT(rows, data)


@strawberry.type
class LST:
    ID_LST: str
    LST_ID_VLST: str
    LST_ID_LST: Optional[str]
    LST_NUM: int
    LST_INDEX: int
    LST_NAME: str
    LST_NAME_SH: Optional[str]


@strawberry.type
class MST:
    ID_MST: str
    MST_NAME: str
    MST_SHIR: float
    MST_DOLG: float


@strawberry.type
class TRS:
    ID_TRS: str
    TRS_SID_GOST: str


@strawberry.type
class MARSH:
    ID_MARSH: str
    MARSH_PR_TEPL: int
    MARSH_NAME: str

    def get_trs(self, stmt):
        d = exec_statement(stmt, id_marsh=int(self.ID_MARSH))
        if len(d.data) == 0:
            return
        return return_strawberry_model(TRS, d.rows, d.data)[0]

    @strawberry.field
    def pric(self) -> Optional[TRS]:
        stmt = text("""
        select t.ID_TRS, t.TRS_SID_GOST from TRS t join MARSH_TRS mt on mt.MARSH_TRS_ID_PRIC = t.ID_TRS where mt.MARSH_TRS_ID_MARSH = :id_marsh
        """)
        return self.get_trs(stmt)

    @strawberry.field
    def auto(self) -> Optional[TRS]:
        stmt = text("""
        select t.ID_TRS, t.TRS_SID_GOST from TRS t join MARSH_TRS mt on mt.MARSH_TRS_ID_TRS = t.ID_TRS where mt.MARSH_TRS_ID_MARSH = :id_marsh
        """)
        return self.get_trs(stmt)


@strawberry.type
class APP_PARAM:
    APP_PARAM_ID_REC: str
    APP_PARAM_STR: str
    APP_PARAM_TIP: int


    @strawberry.field
    def marsh(self) -> Optional[MARSH]:

        if self.APP_PARAM_TIP != 8750:
            return
        stmt = text("""
            select m.ID_MARSH, m.MARSH_PR_TEPL, m.MARSH_NAME from MARSH m join MARSH_TRS mt on m.ID_MARSH = mt.MARSH_TRS_ID_MARSH where ID_MARSH_TRS = :id_marsh_trs 
        """)
        d = exec_statement(stmt, id_marsh_trs=int(self.APP_PARAM_STR))
        return return_strawberry_model(MARSH, d.rows, d.data)[0]

    @strawberry.field
    def mst(self) -> Optional[MST]:

        if self.APP_PARAM_TIP not in [8668]:
            return
        stmt = text(f"""
        select ID_MST, MST_NAME, MST_SHIR, MST_DOLG from MST where ID_MST = :id_mst
        """)
        d = exec_statement(stmt, id_mst=int(self.APP_PARAM_STR))
        return return_strawberry_model(MST, d.rows, d.data)[0]


@strawberry.type
class APP_EVENT:
    ID_APP_EVENT: str
    APP_EVENT_ID_SOTR: str
    APP_EVENT_ID_REC: str
    APP_EVENT_VID: int
    APP_EVENT_TIP: int
    APP_EVENT_TEXT: str
    APP_EVENT_DATA: str
    APP_EVENT_PARAM: str
    APP_EVENT_DT: str


@strawberry.type
class DB:

    @strawberry.field
    def app_event(self, user_id: str) -> list[APP_EVENT]:
        stmt = text("select  * from APP_EVENT where APP_EVENT_ID_SOTR = :user_id")
        d = exec_statement(stmt, user_id=user_id)
        return return_strawberry_model(APP_EVENT, d.rows, d.data)

    @strawberry.field
    def param(self, info: strawberry.Info, user_id: Optional[str] = None, id_rec: Optional[str] = None) -> list[
        APP_PARAM]:

        if all(x is None for x in [user_id, id_rec]):
            raise Exception("Argument error. userId or idRec should be provided.")
        if user_id is not None:
            stmt = text(
                "select p.* from APP_PARAM p join APP_TASK t on t.ID_APP_TASK = p.APP_PARAM_ID_REC where t.APP_TASK_ID_SOTR = :id_sotr")
            d = exec_statement(stmt, id_sotr=int(user_id))
        else:
            stmt = text("select * from APP_PARAM where APP_PARAM_ID_REC = :id_rec")
            d = exec_statement(stmt, id_rec=int(id_rec))
        returned_list = return_strawberry_model(APP_PARAM, d.rows, d.data)

        # selections = info.selected_fields[0].selections
        # db_selected_fields = ["p.*"]
        #
        # # Get selection List of field
        # if 'marsh' in [x.name for x in selections]:
        #     sub_query = "join MARSH_TRS mt on cast(p.APP_PARAM_STR as d_bigint) = mt.ID_MARSH_TRS join MARSH m on m.ID_MARSH = mt.MARSH_TRS_ID_MARSH"
        #     db_selected_fields.extend("m." + x for x in MARSH.__annotations__ if MARSH.__annotations__[x] in [str, int])

        return returned_list
