from pydantic import BaseModel
from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic
from models.auth.Permission import Permission
from schemas.auth.FunctionSchema import FunctionBase

PermissionBase = sqlalchemy_to_pydantic(Permission)


class PermissionBase(PermissionBase):
    pass


class PermissionsResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: list[PermissionBase]


class PermissionDetails(BaseModel):
    permission: PermissionBase
    functions: list[FunctionBase]


class PermissionPost(BaseModel):
    name: str
