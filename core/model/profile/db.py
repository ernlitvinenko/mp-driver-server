from pydantic import BaseModel


class ProfileDB(BaseModel):
    id: int
    full_name: str
    phone_number: str


