import typing
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Union

import strawberry

from core.model.task.enums import MarshTemperatureProperty
from core.storage import task


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


@strawberry.type
class Query:

    @strawberry.field
    def tasks(self, user_id: str) -> list['AppTaskQL']:
        tasks = task.fetch_tasks_with_subtasks(user_id=int(user_id))
        returned_list: list['AppTaskQL'] = []
        for t in tasks:
            updated_task = AppTaskQL(
                id=str(t.id),
                start_pln=t.start_pln,
                end_pln=t.end_pln,
                start_fact=t.start_fact,
                end_fact=t.end_fact,
                status=t.status.value,
                task_type=t.task_type.value,
                text=t.text,
                route=MarshQL(
                    id=str(t.route.id),
                    temperature_property=t.route.temperature_property.value,
                    name=t.route.name,
                    trailer=TRSQL(
                        id=str(t.route.trailer.id),
                        gost=t.route.trailer.gost
                    ) if t.route.trailer else None,
                    truck=TRSQL(
                        id=str(t.route.truck.id),
                        gost=t.route.truck.gost
                    ) if t.route.truck else None,
                ) if t.route else None,
                events=[EventQl(
                    id=e.id,
                    type=e.type,
                    text=e.text,
                    event_data=e.event_data,
                    event_datetime=e.event_datetime
                ) for e in t.events]
            )
            returned_list.append(updated_task)

        return returned_list


@strawberry.type
class AppTaskQL:
    id: str
    start_pln: datetime
    end_pln: datetime
    start_fact: datetime | None
    end_fact: datetime | None
    status: StatusEnumQl
    task_type: TaskTypeEnumQl
    text: str

    events = []
    subtasks = []
    route = None


@strawberry.type
class MarshQL:
    id: str
    temperature_property: MarshTemperaturePropertyQl
    name: str
    trailer: typing.Optional['TRSQL'] = None
    truck: typing.Optional['TRSQL'] = None


@strawberry.type
class TRSQL:
    id: str | None
    gost: str | None


@strawberry.type
class EventQl:
    id: int
    type: str
    text: str
    event_data: dict
    event_datetime: datetime


schema = strawberry.Schema(query=Query)
