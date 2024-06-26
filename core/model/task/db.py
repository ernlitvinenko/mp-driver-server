import datetime
import typing
from typing import Union

from pydantic import BaseModel, Field, ConfigDict, AliasGenerator, Json
from pydantic.alias_generators import to_camel

from .enums import StatusEnum, TaskTypeEnum, SubtaskTypeEnum, MarshTemperatureProperty

general_model_config = ConfigDict(alias_generator=AliasGenerator(serialization_alias=to_camel))


class DBModel(BaseModel):
    model_config = general_model_config
    id: int

    def __hash__(self):
        return self.id


class DBSubTask(DBModel):
    start_pln: datetime.datetime
    end_pln: datetime.datetime
    start_fact: datetime.datetime | None
    end_fact: datetime.datetime | None
    status: StatusEnum
    task_type: SubtaskTypeEnum
    text: str

    station: typing.Optional['DBMST'] = None


class DBAppTask(DBModel):
    profile_id: int = Field(exclude=True)
    start_pln: datetime.datetime
    end_pln: datetime.datetime
    start_fact: datetime.datetime | None
    end_fact: datetime.datetime | None
    status: StatusEnum
    task_type: TaskTypeEnum
    text: str

    events: list['DBEvent'] = []
    subtasks: list[DBSubTask] | None = []
    route: 'DBMarsh' = None


class DBMarsh(DBModel):
    temperature_property: MarshTemperatureProperty
    name: str

    parent_id: int = Field(default=0, exclude=True)

    trailer: Union['DBTRS', None]
    truck: Union['DBTRS', None]


class DBTRS(DBModel):
    gost: str | None
    parent_id: int = Field(default=0, exclude=True)


class DBMST(DBModel):
    name: str
    location: 'Location'
    parent_id: int = Field(default=0, exclude=True)


class Location(BaseModel):
    lat: float
    lon: float
    parent_id: int = Field(default=0, exclude=True)


class DBEvent(DBModel):
    id: int
    type: str
    text: str
    parent_id: int = Field(default=0, exclude=True)
    event_data: list | Json
    event_datetime: datetime.datetime
