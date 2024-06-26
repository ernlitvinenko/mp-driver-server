import datetime

from pydantic import BaseModel, Field

from core.model.task.enums import StatusEnum


class UpdTaskData(BaseModel):
    task_id: int
    dt: datetime.datetime
    status: StatusEnum
    error_text: str | None = Field(max_length=1024, default=None)


class UpdTaskRequest(BaseModel):
    data: list[UpdTaskData]


class SetTaskStatusActiveRequest(BaseModel):
    task_id: int
    dt_start: datetime.datetime = Field(default_factory=datetime.datetime.now)


class SetSubtaskStatusRequest(BaseModel):
    subtask_id: int
    finished_dt: datetime.datetime = Field(default_factory=datetime.datetime.now)
