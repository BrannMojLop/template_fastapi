from pydantic import BaseModel, EmailStr
from typing import Optional


class User_Group(BaseModel):
    name: str


class Update_User_Group(BaseModel):
    id: int
    name: str
