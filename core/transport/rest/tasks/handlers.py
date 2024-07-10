from typing import Union, Callable

from fastapi import APIRouter, Depends, Path

from core.errors.auth.errors import no_task_for_current_user
from core.errors.task.errors import unavailable_status, should_provide_error_text_with_cancelled_status, \
    update_task_by_chain_failed
from core.helpers.profile_helpers import get_user_from_token
from core.model.profile.db import ProfileDB
from core.model.task.db import DBAppTask, DBSubTask, DBEvent
from core.model.task.enums import StatusEnum
from core.model.task.requests import SetTaskStatusActiveRequest, SetSubtaskStatusRequest, UpdTaskRequest, UpdTaskData
from core.storage import task_storage

from core.model.task.db2 import MPAppTaskDB

router = APIRouter(prefix="/tasks", tags=["Tasks and subtasks"])


# @router.get("/test", description="Fetch Task for authenticated user")
# async def get_task_test(user: ProfileDB = Depends(get_user_from_token)) -> list[MPAppTaskDB]:
#     return MPAppTaskDB.fetch_all()


@router.get("", description="Fetch Task for authenticated user")
async def get_tasks(user: ProfileDB = Depends(get_user_from_token)) -> list[DBAppTask]:
    return task_storage.fetch_tasks_with_subtasks(user.id)


@router.post("")
async def upd_task(req: UpdTaskRequest, user: ProfileDB = Depends(get_user_from_token)) -> list[DBAppTask]:
    print(req)
    def check_task_in_progress(e: UpdTaskData, t: DBAppTask):
        t.subtasks.sort(key=lambda u: u.start_pln)
        try:
            next(x for x in req.data if x.status == StatusEnum.IN_PROGRESS and x.task_id == t.subtasks[0].id)
        except StopIteration:
            raise Exception("Chain Failed")

    def check_task_completed(e: UpdTaskData, t: DBAppTask):
        t.subtasks.sort(key=lambda u: u.start_pln)
        try:
            next(x for x in req.data if x.status == StatusEnum.COMPLETED and x.task_id == t.subtasks[-1].id)
        except StopIteration:
            raise Exception("Chain Failed")

    def check_sbt_in_progress(e: UpdTaskData, sbt: DBSubTask):
        main_task = next(t for t in tasks for s in t.subtasks if s.id == sbt.id)
        main_task.subtasks.sort(key=lambda u: u.start_pln)
        try:
            if sbt.id == main_task.subtasks[0].id:
                next(x for x in req.data if x.status == StatusEnum.IN_PROGRESS and x.task_id == main_task.id)
            else:
                prev_idx = main_task.subtasks.index(sbt) - 1
                next(ev for ev in req.data if ev.task_id == main_task.subtasks[prev_idx].id and ev.status in ( StatusEnum.COMPLETED, StatusEnum.CANCELLED))
        except StopIteration as exc:
            update_task_by_chain_failed(exc)


    def check_sbt_completed(e: UpdTaskData, sbt: DBSubTask):
        main_task = next(t for t in tasks for s in t.subtasks if s.id == sbt.id)
        main_task.subtasks.sort(key=lambda u: u.start_pln)

        try:
            if sbt.id == main_task.subtasks[-1].id:
                next(ev for ev in req.data if ev.task_id == main_task.id and ev.status == StatusEnum.COMPLETED)
            else:
                next_idx = main_task.subtasks.index(sbt) + 1
                next(ev for ev in req.data if
                     ev.task_id == main_task.subtasks[next_idx].id and ev.status == StatusEnum.IN_PROGRESS)
        except StopIteration as exc:
            update_task_by_chain_failed(exc)

    steps: dict[Union[type[DBAppTask], type[DBSubTask]], dict[
        StatusEnum, Callable[[UpdTaskData, Union[DBAppTask, DBSubTask]], None]]] = {
        DBAppTask: {
            StatusEnum.IN_PROGRESS: check_task_in_progress,
            StatusEnum.COMPLETED: check_task_completed,
        },
        DBSubTask: {
            StatusEnum.COMPLETED: check_sbt_completed,
            StatusEnum.CANCELLED: check_sbt_completed,
            StatusEnum.IN_PROGRESS: check_sbt_in_progress,
        }
    }

    tasks = task_storage.fetch_tasks_with_subtasks(user.id)
    available_tasks_ids = [x.id for x in tasks] + [sbt.id for t in tasks for sbt in t.subtasks]

    req.data.sort(key=lambda u: u.dt)
    if len(req.data) <= 1 and len(req.data) % 2 != 0:
        raise Exception("should provide the pairs of arguments")

    for idx, event in enumerate(req.data):
        # Сделать проверку, как только заканчивается событие с этим же временем должно начинаться новое
        #  т.е. Нельзя передать только начало события или только конец
        #  Если передаем InProgress и идентификатор является задачей - должны передать InProgress для подзадачи
        #  Если передаем InProgress и идентификатор является подзадачей - должны передать Completed или Canceled
        #  для подзадачи

        # Цепочка имеет валидна, если имеет след вид:
        #  task (InProgress) -> subtask (InProgress);
        #   subtask(Completed/Cancelled) -> subtask(InProgress);
        #   subtask(Completed/Cancelled) -> task(Completed)

        # НЕОБХОДИМО ДЕЛАТЬ И ОБРАТНУЮ ПРОВЕРКУ
        #   если sbt(InProgress), то должно существовать task(InProgress) или sbt(Completed/Cancelled)
        #   если task(Completed), то последняя подзадача sbt по APP_TASK_DT_START_PLN должна быть передана

        if event.task_id not in available_tasks_ids:
            no_task_for_current_user()
        if event.status == StatusEnum.NOT_DEFINED:
            unavailable_status()
        if event.status == StatusEnum.CANCELLED and (event.error_text is None or event.error_text.strip() == ''):
            should_provide_error_text_with_cancelled_status()

        # проверяем является ли событие подзадачей
        is_sbt = event.task_id not in (x.id for x in tasks)
        task_: DBAppTask | DBSubTask = next(x for x in tasks if x.id == event.task_id) if not is_sbt else next(
            sbt for x in tasks for sbt in x.subtasks if sbt.id == event.task_id)

        try:
            steps[type(task_)][event.status](event, task_)
        except KeyError as exc:
            update_task_by_chain_failed(exc)

    [task_storage.update_task(event, user.id) for event in req.data]
    return task_storage.fetch_tasks_with_subtasks(user.id)


@router.get("/planned")
async def get_planned_tasks(user: ProfileDB = Depends(get_user_from_token)) -> list[DBAppTask]:
    # TODO Rebuild this method to fetch only planned tasks
    tasks = task_storage.fetch_tasks_with_subtasks(user_id=user.id)
    return [x for x in tasks if x.status == StatusEnum.NOT_DEFINED]


@router.get("/active")
async def get_active_task(user: ProfileDB = Depends(get_user_from_token)) -> DBAppTask | dict:
    # TODO Rebuild this method to fetch only active tasks
    tasks = task_storage.fetch_tasks_with_subtasks(user_id=user.id)
    try:
        return next(x for x in tasks if x.status == StatusEnum.IN_PROGRESS)
    except StopIteration:
        return {}


@router.get("/completed")
async def get_active_task(user: ProfileDB = Depends(get_user_from_token)) -> list[DBAppTask]:
    # TODO Rebuild this method to fetch only active tasks
    tasks = task_storage.fetch_tasks_with_subtasks(user_id=user.id)
    return [x for x in tasks if x.status == StatusEnum.COMPLETED]


# @router.post('/active')
# async def change_task_to_active(req: SetTaskStatusActiveRequest, user: ProfileDB = Depends(get_user_from_token)):
#     tasks = task.fetch_tasks_for_user(user_id=user.id)
#     for t in tasks:
#         if t.status == StatusEnum.IN_PROGRESS:
#             return t.model_dump(mode='json', exclude={'events', 'subtasks', 'route'})
#
#     for t in tasks:
#         if t.id == req.task_id:
#             task.set_task_to_active_state(task_id=t.id, profile_id=user.id, dt=req.dt_start)
#             t.status = StatusEnum.IN_PROGRESS
#             return t
#
#     no_task_for_current_user()


@router.get("/{task_id}/subtasks")
async def get_subtasks(user: ProfileDB = Depends(get_user_from_token), task_id: int = Path()) -> list[DBSubTask]:
    # TODO Rebuild this method to fetch only subtasks
    tasks = task_storage.fetch_tasks_with_subtasks(user_id=user.id)
    try:
        t = next(x for x in tasks if x.id == task_id)
        return t.subtasks
    except StopIteration:
        no_task_for_current_user()


@router.post("/subtask")
async def set_status_to_subtask(req_data: SetSubtaskStatusRequest,
                                user: ProfileDB = Depends(get_user_from_token)) -> DBSubTask:
    tasks = task_storage.fetch_tasks_with_subtasks(user_id=user.id)
    try:
        subtask = next(subtask for t in tasks for subtask in t.subtasks if subtask.id == req_data.subtask_id)

        task_storage.set_subtask_to_completed(subtask_id=subtask.id, profile_id=user.id, dt=req_data.finished_dt)
        subtask.status = StatusEnum.COMPLETED
        return subtask

    except StopIteration:
        no_task_for_current_user()


@router.get("/{task_id}/events")
async def get_events(user: ProfileDB = Depends(get_user_from_token), task_id: int = Path()) -> list[DBEvent]:
    # TODO Rebuild this method to fetch only events
    tasks = task_storage.fetch_tasks_with_subtasks(user_id=user.id)
    try:
        t = next(x for x in tasks if x.id == task_id)
        return [x for x in t.events if x.type == "Change"]
    except StopIteration:
        no_task_for_current_user()
