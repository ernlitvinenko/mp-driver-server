from pydantic import BaseModel


class AppNoteDB(BaseModel):
    id: int
    user_id: int
    task_id: int
    note_status: int
    tip: int
    text: str
