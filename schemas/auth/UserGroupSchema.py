from pydantic import BaseModel
from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic
from models.auth.UserGroup import UserGroup
from schemas.auth.PermissionSchema import PermissionBase

UserGroupModel = sqlalchemy_to_pydantic(UserGroup)


class UserGroupBase(UserGroupModel):
    pass


class UserGroupsResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: list[UserGroupBase]


class UserGroupDetails(BaseModel):
    group: UserGroupBase
    permissions: list[PermissionBase]


class UserGroupModeSelect(BaseModel):
    label: str
    value: int


class UserGroupPost(BaseModel):
    name: str


class UserGroupForId(BaseModel):
    id: UserGroupBase
