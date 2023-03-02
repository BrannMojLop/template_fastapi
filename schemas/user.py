from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    id: Optional[int]
    email: EmailStr
    phone: str
    name: str
    last_name_first: str
    last_name_second: str
    password: Optional[str]
    user_group: Optional[int]


class UserUpdate(BaseModel):
    email: EmailStr
    phone: str
    name: str
    last_name_first: str
    last_name_second: str
    user_group: Optional[int]


class User_Login(BaseModel):
    email: EmailStr
    password: str


class User_Reset_Password(BaseModel):
    password: str
    access_token: str


class User_Validation(BaseModel):
    token: str
    password: str
