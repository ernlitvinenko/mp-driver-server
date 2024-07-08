from .base import BaseStorage
from .profile_storage import Storage as ProfileStorage
from .task_storage import Storage as TaskStorage
from .note_storage import Storage as NoteStorage

base_storage = BaseStorage()
profile_storage = ProfileStorage()
task_storage = TaskStorage()
note_storage = NoteStorage()

