from typing import List
from pydantic import BaseModel, validator
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from models.UserGroup import UserGroup
from schemas.PermissionSchema import PermissionBase

UserGroupBase = sqlalchemy_to_pydantic(UserGroup)


class UserGroupsResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: List[UserGroupBase]


class UserGroupDetails(BaseModel):
    group: UserGroupBase
    permissions: List[PermissionBase]


class UserGroupModeSelect(BaseModel):
    label: str
    value: int


class UserGroupPost(BaseModel):
    name: str

    @validator("name")
    def name_validate(cls, value):
        if len(value) < 3:
            raise ValueError("The 'name' parameter must have at least 3 characters")
        return value.title()


class UserGroupForId(BaseModel):
    id: UserGroupBase
