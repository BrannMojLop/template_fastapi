from typing import List
from pydantic import BaseModel, validator
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from models.Permission import Permission
from schemas.FunctionSchema import FunctionBase

PermissionBase = sqlalchemy_to_pydantic(Permission)


class PermissionsResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: List[PermissionBase]


class PermissionDetails(BaseModel):
    permission: PermissionBase
    functions: List[FunctionBase]


class PermissionPost(BaseModel):
    name: str

    @validator("name")
    def name_validate(cls, value):
        if len(value) < 3:
            raise ValueError("The 'name' parameter must have at least 3 characters")
        return value.title()
