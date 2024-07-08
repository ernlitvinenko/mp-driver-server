import datetime
import json
from typing import Optional

import sqlalchemy
from sqlalchemy import text
from .base import BaseStorage
from ..model.note.db import AppNoteDB



class Storage(BaseStorage):
    def fetch_all_notes_for_user(self, user_id: int):
        stmt = text("""
            select * from APP_NOTE where APP_NOTE_ID_SOTR = :user_id and APP_NOTE_DEL = 0;
        """)
        with self.get_session() as session:
            session: sqlalchemy.Connection
            res = [x.row_to_type() for x in session.execute(stmt, {
                "user_id": user_id
            }).fetchall()]
        return [AppNoteDB(id=row.ID_APP_NOTE, user_id=row.APP_NOTE_ID_SOTR, task_id=row.APP_NOTE_ID_APP_TASK,
                          note_status=row.APP_NOTE_STATUS, tip=row.APP_NOTE_TIP, text=row.APP_NOTE_TEXT) for row in res]

    def update_note(self, id: int, status: int, user_id: int):
        stmt = text("""
            insert into APP_EVENT (APP_EVENT_DT, APP_EVENT_ID_SOTR, APP_EVENT_TEXT, APP_EVENT_DATA, APP_EVENT_VID, APP_EVENT_ID_REC) values (current_timestamp, :user_id, 'Изменен статус уведомлений', :event_data, 8797, :note_id)
        """)

        event_data = json.dumps([{"8794": str(status)}], separators=(',', ":"))

        with self.get_session() as session:
            session: sqlalchemy.Connection
            session.execute(stmt, {
                "user_id": user_id,
                "event_data": event_data,
                "note_id": id
            })
            session.commit()

    def create_note(self, user_id: int, note_text: str, time_created: datetime.datetime, task_id: Optional[int] = None):
        stmt = text("""
        insert into APP_EVENT (APP_EVENT_DT, APP_EVENT_ID_SOTR, APP_EVENT_TEXT, APP_EVENT_DATA, APP_EVENT_VID) values (:time_created, :user_id, :text, :event_data, 8795)
        """)

        if (task_id is not None):
            event_data = json.dumps([{"ID_APP_TASK": str(task_id)}], separators=(",", ":"))
        else:
            event_data = None
        with self.get_session() as session:
            session: sqlalchemy.Connection
            session.execute(stmt, {
                "time_created": time_created,
                "user_id": user_id,
                "text": note_text,
                "event_data": event_data
            })
            session.commit()
