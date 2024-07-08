import typing

from core.model.note.db import AppNoteDB
from core.model.task.db import DBAppTask, DBSubTask, DBEvent, DBMarsh, DBTRS, DBMST, Location

from datetime import datetime
from enum import Enum

import strawberry
from strawberry.types import Info
from sqlalchemy import select

from core.model.task.enums import StatusEnum
from core.storage import base_storage, task_storage, note_storage


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
    def tasks(self, user_id: str, is_planned: typing.Optional[bool] = False, is_completed: typing.Optional[bool] = False) -> list['AppTaskQL']:
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
    def notes(self, user_id: str) -> list['AppNoteQL']:
        return note_storage.fetch_all_notes_for_user(int(user_id))

    @strawberry.field
    def subtask(self, user_id: str, subtask_id: str) -> typing.Optional['SubtaskQL']:
        try:
            return next(s for t in task_storage.fetch_tasks_with_subtasks(int(user_id)) for s in t.subtasks if
                        s.id == int(subtask_id))
        except StopIteration:
            return None


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
    task_type: int
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
    task_type: int
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


schema = strawberry.Schema(query=Query)
