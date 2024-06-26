import datetime
import json
import typing
from enum import Enum

import sqlalchemy
from sqlalchemy import text, TextClause
from typing_extensions import deprecated

from core.model.task.db import DBAppTask, DBSubTask, DBMarsh, DBTRS, DBMST, Location, DBEvent
from .base import BaseStorage
from ..model.task.enums import StatusEnum
from ..model.task.requests import UpdTaskData


class _STMTS(Enum):
    FETCH_TASKS_WITH_SUBTASKS = text(f"""
select t1.ID_APP_TASK,                                          -- 0
       t1.APP_TASK_ID_SOTR,                                     -- 1
       t1.APP_TASK_ID_APP_TASK,                                 -- 2
       t1.APP_TASK_DT_START_PLN,                                -- 3
       t1.APP_TASK_DT_END_PLN,                                  -- 4
       t1.APP_TASK_DT_START_FACT,                               -- 5
       t1.APP_TASK_DT_END_FACT,                                 -- 6
       lst_status.LST_NAME_SH,                                  -- 7
       lst_tip.LST_NAME_SH,                                     -- 8
       t1.APP_TASK_TEXT,                                        -- 9

       lst_param_tip.LST_NAME_SH as param_tip,                  -- 10

       --        marsh trs
       trs_1.ID_TRS              as truck_id,                   -- 11
       trs_1.TRS_SID_GOST        as truck_gost,                 -- 12
       trs_2.ID_TRS              as trailer_id,                 -- 13
       trs_2.TRS_SID_GOST        as trailer_gost,               -- 14
       m.ID_MARSH                as marsh_id,                   -- 15
       m.MARSH_PR_TEPL           as marsh_temperature_property, --16
       m.MARSH_NAME              as marsh_name,                 -- 17

       --        MST
       mst.ID_MST,                                              -- 18
       mst.MST_NAME,                                            -- 19
       mst.MST_SHIR,                                            -- 20
       mst.MST_DOLG,                                            -- 21

       -- EVENT
       event.ID_APP_EVENT,                                      -- 22
       event.LST_NAME_SH,                                   -- 23
       event.APP_EVENT_TEXT,                                     -- 24,
        event.APP_EVENT_ID_REC, -- 25
         event.APP_EVENT_DT,  -- 26
         event.APP_EVENT_DATA -- 27

from APP_TASK t1
         left join LST lst_status
                   on t1.APP_TASK_STATUS = lst_status.ID_LST
         left join LST lst_tip on t1.APP_TASK_TIP = lst_tip.ID_LST
         left join APP_PARAM param on param.APP_PARAM_ID_REC = t1.ID_APP_TASK and param.APP_PARAM_DEL = 0
         LEFT JOIN LST lst_param_tip on param.APP_PARAM_TIP = lst_param_tip.ID_LST
         left join MARSH_TRS mt on param.APP_PARAM_STR = mt.ID_MARSH_TRS and lst_param_tip.LST_NAME_SH = 'ID_MARSH_TRS'
         left join TRS trs_1 on mt.MARSH_TRS_ID_TRS = trs_1.ID_TRS
         left join TRS trs_2 on mt.MARSH_TRS_ID_PRIC = trs_2.ID_TRS
         left join MARSH m on mt.MARSH_TRS_ID_MARSH = m.ID_MARSH
         left join MST mst on param.APP_PARAM_STR = mst.ID_MST and lst_param_tip.LST_NAME_SH = 'ID_MST'
         left join (select ID_APP_EVENT, LST_NAME_SH, APP_EVENT_TEXT, APP_EVENT_ID_REC, APP_EVENT_DT, APP_EVENT_DATA from APP_EVENT join LST on ID_LST = APP_EVENT_VID where APP_EVENT_DEL = 0) event
             on event.APP_EVENT_ID_REC = t1.ID_APP_TASK
where t1.APP_TASK_DEL = 0
  and t1.APP_TASK_ID_SOTR = :user_id;
        """)
    FETCH_NEXT_SUBTASK_FOR_TASK = text(
        f"""select ID_APP_TASK from app_task where APP_TASK_ID_APP_TASK = :task_id and APP_TASK_ID_APP_TASK != ID_APP_TASK AND APP_TASK_DEL = 0 and APP_TASK_STATUS not in (8681, 8682) order by APP_TASK_DT_START_PLN""")

    INSERT_EVENT = text("""
           INSERT into APP_EVENT (
        APP_EVENT_ID_SOTR,
         APP_EVENT_ID_REC,
          APP_EVENT_DT,
           APP_EVENT_DATA,
            APP_EVENT_TEXT,
             APP_EVENT_VID, APP_EVENT_PARAM) values (:user_id,
              :rec_id,
               :event_dt,
                :event_data,
                 :event_text,
                  8678, :event_params)
        """)


def generate_event_stmt(profile_id: int, task_id: int, event_dt: datetime.datetime, event_text: str,
                        event_data: dict[str, str], event_params: dict[str, str] | None = None) -> tuple[
    TextClause, dict[str, typing.Any]]:
    return _STMTS.INSERT_EVENT.value, {"user_id": profile_id,
                                       "rec_id": task_id,
                                       "event_dt": event_dt,
                                       "event_text": event_text,
                                       "event_data": json.dumps([event_data], separators=(',', ':')),
                                       "event_params": json.dumps([event_params],
                                                                  separators=(',', ":")) if event_params else None
                                       }


class Storage(BaseStorage):

    def generate_station(self, row: tuple) -> typing.Optional[DBMST]:
        return DBMST(id=row[18], name=row[19], location=Location(lat=row[20], lon=row[21], parent_id=row[18]),
                     parent_id=row[0])

    def generate_truck(self, row: tuple) -> typing.Optional[DBTRS]:
        if row[11] is not None and row[11]:
            return DBTRS(id=row[11], gost=row[12], parent_id=row[15])

    def generate_trailer(self, row: tuple) -> typing.Optional[DBTRS]:
        if row[13] is not None and row[13] != 0:
            return DBTRS(id=row[13], gost=row[14], parent_id=row[16])

    def generate_route(self, row: tuple) -> typing.Optional[DBMarsh]:
        return DBMarsh(id=row[15], temperature_property=row[16], name=row[17],
                       trailer=self.generate_trailer(row),
                       truck=self.generate_truck(row), parent_id=row[0])

    def generate_event(self, row):
        return DBEvent(id=row[22], type=row[23], text=row[24], parent_id=row[0], event_datetime=row[26],
                       event_data=row[27])

    def generate_task(self, row):
        return DBAppTask(id=row[0], profile_id=row[1], start_pln=row[3], end_pln=row[4], start_fact=row[5],
                         end_fact=row[6], status=row[7], task_type=row[8], text=row[9])

    def generate_subtask(self, row):
        return DBSubTask(id=row[0], parent_id=row[2], start_pln=row[3], end_pln=row[4], start_fact=row[5],
                         end_fact=row[6], status=row[7], task_type=row[8], text=row[9])

    def fetch_tasks_with_subtasks(self, user_id: int) -> list[DBAppTask]:
        stmt = _STMTS.FETCH_TASKS_WITH_SUBTASKS.value
        with self.get_session() as cur:
            cur: sqlalchemy.Connection
            res = cur.execute(stmt, {"user_id": user_id}).fetchall()

            tasks = list(set(self.generate_task(row) for row in res if row[0] == row[2]))
            for task in tasks:
                task.subtasks = list(
                    set(self.generate_subtask(row) for row in res if row[0] != row[2] and row[2] == task.id))
                task.events = list(
                    set(self.generate_event(row) for row in res if row[22] is not None and row[25] == task.id))
                task.subtasks.sort(key=lambda u: u.start_pln)
                task.events.sort(key=lambda u: u.event_datetime)

                for subtask in task.subtasks:
                    subtask.station = next(self.generate_station(row) for row in res if
                                           row[18] is not None and row[0] == subtask.id)

                task.route = next(self.generate_route(row) for row in res if row[0] == task.id and row[15] is not None)

            tasks.sort(key=lambda u: u.start_pln)
            return tasks

    @deprecated("DEPRECATED: use fetch_tasks_with_subtasks instead")
    def fetch_task_by_id(self, task_id: int) -> typing.Optional[DBAppTask]:
        stmt = text("""
       select first 1 t1.ID_APP_TASK,
 t1.APP_TASK_ID_SOTR,
  t1.APP_TASK_ID_APP_TASK,
   t1.APP_TASK_DT_START_PLN,
    t1.APP_TASK_DT_END_PLN,
     t1.APP_TASK_DT_START_FACT,
      t1.APP_TASK_DT_END_FACT,
       lst_status.LST_NAME_SH,
        lst_tip.LST_NAME_SH,
         t1.APP_TASK_TEXT from APP_TASK t1
    left join LST lst_status on t1.APP_TASK_STATUS = lst_status.ID_LST
    left join LST lst_tip on t1.APP_TASK_TIP = lst_tip.ID_LST
where 
t1.APP_TASK_DEL = 0 and
t1.ID_APP_TASK = :task_id and
t1.ID_APP_TASK = t1.APP_TASK_ID_APP_TASK; 
        """)
        with self.get_session() as cur:
            cur: sqlalchemy.Connection
            res = cur.execute(stmt, {"task_id": task_id}).fetchone()
        return res if res is None else DBAppTask(id=res[0], profile_id=res[1], start_pln=res[3], end_pln=res[4],
                                                 start_fact=res[5], end_fact=res[6], status=res[7], task_type=res[8],
                                                 text=res[9])

    @deprecated("DEPRECATED: use fetch_tasks_with_subtasks instead")
    def fetch_tasks_for_user(self, user_id: int, limit: int = 10, offset: int = 0) -> list[DBAppTask]:
        stmt = text("""
select first :limit skip :offset t1.ID_APP_TASK,
 t1.APP_TASK_ID_SOTR,
  t1.APP_TASK_ID_APP_TASK,
   t1.APP_TASK_DT_START_PLN,
    t1.APP_TASK_DT_END_PLN,
     t1.APP_TASK_DT_START_FACT,
      t1.APP_TASK_DT_END_FACT,
       lst_status.LST_NAME_SH,
        lst_tip.LST_NAME_SH,
         t1.APP_TASK_TEXT from APP_TASK t1
    left join LST lst_status on t1.APP_TASK_STATUS = lst_status.ID_LST
    left join LST lst_tip on t1.APP_TASK_TIP = lst_tip.ID_LST
where 
t1.APP_TASK_DEL = 0 and 
t1.ID_APP_TASK = t1.APP_TASK_ID_APP_TASK and
t1.APP_TASK_ID_SOTR = :user_id;
        """)
        with self.get_session() as session:
            session: sqlalchemy.Connection
            res = session.execute(stmt, {"limit": limit, "offset": offset, "user_id": user_id}).fetchall()

        return [DBAppTask(id=row[0], profile_id=row[1], start_pln=row[3], end_pln=row[4],
                          start_fact=row[5], end_fact=row[6], status=row[7], task_type=row[8], text=row[9]) for row
                in res]

    def update_task(self, event: UpdTaskData, profile_id: int):
        with self.get_session() as session:
            session: sqlalchemy.Connection

            status_id = session.execute(text("""
            select first 1 ID_LST from LST where LST_NAME_SH = :status_val and LST_DEL = 0 
            """), {"status_val": event.status.value}).fetchone()[0]

            data = {"8794": f"{status_id}"}

            if event.status == StatusEnum.CANCELLED:
                data["error"] = event.error_text

            session.execute(*generate_event_stmt(profile_id, event.task_id, event.dt,
                                                 f"Установлен новый статус {"задачи" if self.fetch_task_by_id(event.task_id) else "подзадачи"}: {event.status.value}", event_data=data))
            session.commit()
