import json
import typing

from core.model.note.db import AppNoteDB
from core.model.task.db import DBAppTask, DBSubTask, DBEvent, DBMarsh, DBTRS, DBMST, Location

from datetime import datetime
from enum import Enum

import strawberry
from strawberry.types import Info
from sqlalchemy import select, text, insert, TableClause, ColumnClause

from core.model.task.db2 import MPAppEventDB
from core.model.task.enums import StatusEnum
from core.storage import base_storage, task_storage, note_storage
from core.transport.graphql.db_schema import DB, APP_EVENT


@strawberry.enum
class StatusEnumQl(Enum):
    CANCELLED = "Cancelled"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    NOT_DEFINED = "NotDefined"


@strawberry.enum
class TaskTypeEnumQl(Enum):
    MOV_MARSH = "MovMarsh"


@strawberry.enum
class MarshTemperaturePropertyQl(Enum):
    HOT = 1
    COLD = 2
    UNDEFINED = 0


@strawberry.enum
class MarshTemperaturePropertyQL(Enum):
    HOT = 1
    COLD = 2
    UNDEFINED = 0


@strawberry.type
class Query:

    @strawberry.field
    def db(self) -> DB:
        return DB()

    @strawberry.field
    def tasks(self, user_id: str, is_planned: typing.Optional[bool] = False,
              is_completed: typing.Optional[bool] = False) -> list['AppTaskQL']:
        tasks = task_storage.fetch_tasks_with_subtasks(user_id)

        if is_planned:
            return [x for x in tasks if x.status == StatusEnum.NOT_DEFINED]
        if is_completed:
            return [x for x in tasks if x.status == StatusEnum.COMPLETED]

        return tasks

    @strawberry.field
    def task(self, user_id: str, task_id: typing.Optional[str] = None, is_active: typing.Optional[bool] = None) -> \
            typing.Optional[
                'AppTaskQL']:
        tasks = task_storage.fetch_tasks_with_subtasks(user_id)

        if task_id is not None:
            try:
                return next(t for t in tasks if t.id == int(task_id))
            except StopIteration:
                return None
        if is_active is not None:
            try:
                return next(t for t in tasks if t.status == StatusEnum.IN_PROGRESS)
            except StopIteration:
                return None

    @strawberry.field
    def count_planned_tasks(self, user_id: str) -> int:
        return len(
            [x for x in task_storage.fetch_tasks_with_subtasks(int(user_id)) if x.status == x.status.NOT_DEFINED])

    @strawberry.field
    def count_completed_tasks(self, user_id: str) -> int:
        return len([x for x in task_storage.fetch_tasks_with_subtasks(int(user_id)) if x.status == x.status.COMPLETED])

    @strawberry.field
    def notes(self, user_id: str) -> list['AppNoteQL']:
        return note_storage.fetch_all_notes_for_user(int(user_id))

    @strawberry.field
    def subtask(self, user_id: str, subtask_id: str) -> typing.Optional['SubtaskQL']:
        try:
            return next(s for t in task_storage.fetch_tasks_with_subtasks(int(user_id)) for s in t.subtasks if
                        s.id == int(subtask_id))
        except StopIteration:
            return None

    @strawberry.field
    def subtasks(self, user_id: str) -> list['SubtaskQL']:
        return [s for t in task_storage.fetch_tasks_with_subtasks(int(user_id)) for s in t.subtasks]


@strawberry.experimental.pydantic.type(model=Location)
class LocationQL:
    lat: float
    lon: float


@strawberry.experimental.pydantic.type(model=DBMST)
class MSTQL:
    name: str
    location: LocationQL


@strawberry.experimental.pydantic.type(model=DBSubTask)
class SubtaskQL:
    id: str
    start_pln: strawberry.auto
    end_pln: strawberry.auto
    start_fact: strawberry.auto
    end_fact: strawberry.auto
    status: StatusEnumQl
    task_type: str
    text: str

    station: typing.Optional[MSTQL] = None


@strawberry.experimental.pydantic.type(model=DBEvent)
class AppEventQL:
    id: str
    type: str
    text: str
    event_datetime: datetime


@strawberry.experimental.pydantic.type(model=DBTRS)
class TRSQL:
    gost: str | None


@strawberry.experimental.pydantic.type(model=DBMarsh)
class AppRouteQL:
    temperature_property: MarshTemperaturePropertyQL
    name: str
    trailer: typing.Optional[TRSQL]
    truck: typing.Optional[TRSQL]


@strawberry.experimental.pydantic.type(model=AppNoteDB)
class AppNoteQL:
    id: str
    user_id: str
    task_id: str
    note_status: int
    tip: int
    text: str


@strawberry.experimental.pydantic.type(model=DBAppTask)
class AppTaskQL:
    id: str
    profile_id: strawberry.auto
    start_pln: strawberry.auto
    end_pln: strawberry.auto
    start_fact: strawberry.auto
    end_fact: strawberry.auto
    status: StatusEnumQl
    task_type: str
    text: strawberry.auto

    events: list[AppEventQL]
    subtasks: list[SubtaskQL]
    route: 'AppRouteQL'

    @strawberry.field
    def active_subtask(self) -> typing.Optional[SubtaskQL]:
        try:
            return next(x for x in self.subtasks if x.status == x.status.IN_PROGRESS)
        except StopIteration:
            return None



@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_event(self,
    APP_EVENT_ID_SOTR: str,
    APP_EVENT_ID_REC: str,
    APP_EVENT_VID: int,
    APP_EVENT_TIP: int,
    APP_EVENT_TEXT: str,
    APP_EVENT_DATA: str,
    APP_EVENT_DT: str) -> APP_EVENT:
        with base_storage.get_session() as session:
            stmt = insert(MPAppEventDB).values(
                **{
                    "APP_EVENT_ID_SOTR": int(APP_EVENT_ID_SOTR),
                    "APP_EVENT_ID_REC": int(APP_EVENT_ID_REC),
                    "APP_EVENT_VID": int(APP_EVENT_VID),
                    "APP_EVENT_TIP": int(APP_EVENT_TIP),
                    "APP_EVENT_TEXT": APP_EVENT_TEXT,
                    "APP_EVENT_DATA": json.dumps(json.loads(APP_EVENT_DATA), separators=(',', ":")),
                    "APP_EVENT_DT": datetime.fromtimestamp(int(APP_EVENT_DT) / 1000),
                }
            )
            row = session.execute(stmt)
            session.commit()
            row = session.execute(text("""
                select * from APP_EVENT where ID_APP_EVENT = :idx
            """), {"idx": row.inserted_primary_key_rows[0][0]})
            data = row.fetchone()

        return APP_EVENT(**{row._metadata.keys._keys[idx].upper(): elem for idx, elem in enumerate(data) if
                             row._metadata.keys._keys[idx].upper() in APP_EVENT.__annotations__})


schema = strawberry.Schema(query=Query, mutation=Mutation)
