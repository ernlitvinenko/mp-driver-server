from core.model.profile.db import ProfileDB
from core.model.task.db import DBAppTask, DBSubTask, DBEvent, DBMarsh, DBTRS, DBMST, Location
from core.model.task.db2 import MPAppTaskDB, MPMarshTRSDB, MPMSTDB


def fetch_all_tasks(user: ProfileDB) -> list[DBAppTask]:
    table = MPAppTaskDB.get_table()
    tasks = MPAppTaskDB.fetch_all(table.APP_TASK_ID_SOTR == user.id)

    returned_list = []

    for task in tasks:
        if task.is_subtask:
            continue

        subtasks_db = [x for x in tasks if x.is_subtask and x.APP_TASK_ID_APP_TASK == task.ID_APP_TASK]
        subtasks = []

        for subtask in subtasks_db:
            try:
                station_db: MPMSTDB = next(p for p in subtask.params if p.APP_PARAM_TIP == 8668).related_table
                station = DBMST(id=station_db.ID_MST, name=station_db.MST_NAME,
                                location=Location(lat=station_db.MST_SHIR, lon=station_db.MST_DOLG))
            except StopIteration:
                station = None

            subtasks.append(DBSubTask(id=subtask.ID_APP_TASK,
                                      start_pln=subtask.APP_TASK_DT_START_PLN, end_pln=subtask.APP_TASK_DT_END_PLN,
                                      start_fact=subtask.APP_TASK_DT_START_FACT, end_fact=subtask.APP_TASK_DT_END_FACT,
                                      status=subtask.status.LST_NAME_SH,
                                      task_type=subtask.task_type.LST_NAME_SH,
                                      text=subtask.APP_TASK_TEXT,
                                      station=station)
                            )

        events = [
            DBEvent(id=x.ID_APP_EVENT,
                    type=x.event_type.LST_NAME_SH,
                    text=x.APP_EVENT_TEXT,
                    parent_id=task.ID_APP_TASK,
                    event_data=x.event_data,
                    event_datetime=x.APP_EVENT_DT) for x in task.events
        ]

        marsh_trs: MPMarshTRSDB = task.params[0].related_table
        marsh = marsh_trs.marsh
        trs_db = marsh_trs.trs
        trailer_db = marsh_trs.trailer

        trailer = DBTRS(id=trailer_db.ID_TRS, gost=trailer_db.TRS_SID_GOST)
        truck = DBTRS(id=trs_db.ID_TRS, gost=trs_db.TRS_SID_GOST)

        route = DBMarsh(id=marsh.ID_MARSH,
                        temperature_property=marsh.MARSH_PR_TEPL,
                        name=marsh.MARSH_NAME,
                        trailer=trailer,
                        truck=truck
                        )

        returned_list.append(DBAppTask(
            id=task.ID_APP_TASK,
            profile_id=task.APP_TASK_ID_SOTR,
            start_pln=task.APP_TASK_DT_START_PLN,
            end_pln=task.APP_TASK_DT_END_PLN,
            start_fact=task.APP_TASK_DT_START_FACT,
            end_fact=task.APP_TASK_DT_END_FACT,
            status=task.status.LST_NAME_SH,
            task_type=task.task_type.LST_NAME_SH,
            text=task.APP_TASK_TEXT,
            events=events,
            subtasks=subtasks,
            route=route
        ))

    return returned_list
