from pydantic import BaseModel
from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic
from models.auth.Function import Function

FunctionModel = sqlalchemy_to_pydantic(Function)


class FunctionBase(FunctionModel):
    pass


class FunctionsResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: list[FunctionBase]
