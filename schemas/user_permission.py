from pydantic import BaseModel, EmailStr
from typing import Optional


class User_Permission(BaseModel):
    id: Optional[int]
    name: str


class Update_User_Permission(BaseModel):
    id: int
    name: str
