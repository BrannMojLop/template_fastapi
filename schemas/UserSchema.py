import re
from typing import List, Optional, Union
from pydantic import BaseModel, validator
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from models.User import TypeUser, User

UserBaseAuth = sqlalchemy_to_pydantic(User)

UserBase = sqlalchemy_to_pydantic(
    User,
    exclude={
        "password_version",
        "password_hash",
    },
)


class UserExtend(UserBase):
    user_group_name: Optional[str]


class UserPost(UserBase):
    id: Optional[int]

    @validator("name")
    def name_validate(cls, value):
        if len(value) < 3:
            raise ValueError(
                "The 'first_name' parameter must have at least 3 characters"
            )
        return value.title()

    @validator("last_name_first")
    def last_name_first_validate(cls, value):
        if len(value) < 3:
            raise ValueError(
                "The 'first_name' parameter must have at least 3 characters"
            )
        return value.title()

    @validator("last_name_second")
    def last_name_second_validate(cls, value):
        if len(value) < 3:
            raise ValueError(
                "The 'last_name' parameter must have at least 3 characters"
            )
        return value.title()

    @validator("email")
    def validate_email(cls, value):
        if len(value) == 0:
            return None

        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email address")

        return value.lower()

    @validator("phone")
    def phone_validate(cls, value):
        if not value:
            return None

        if re.match(r"^\d{10}$", value):
            return value

        raise ValueError("The 'phone' parameter is not a phone number valid")


class UserUpdate(UserPost):
    name: Optional[str]
    last_name_first: Optional[str]
    last_name_second: Optional[str]
    type: Optional[TypeUser]


class UserResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: List[UserExtend]


class UserPostLogin(BaseModel):
    email: Optional[str] = ""
    phone: Optional[str] = ""
    id: Optional[int] = None
    password: str


class UserChangePassword(BaseModel):
    password: str


class UserAccessToken(BaseModel):
    id: int
    email: Optional[str]
    exp: str
    user_group: Optional[int]
    name: str
    type: str
    phone: Optional[str]
    password_temp: bool
    password_version: int
    access_token: str


class UserValidateToken(UserAccessToken):
    access_token: Optional[str]


class UserForId(BaseModel):
    id: UserBase
