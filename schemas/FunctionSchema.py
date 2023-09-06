from typing import List, Optional
from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from models.Function import Function

FunctionBase = sqlalchemy_to_pydantic(Function)


class FunctionsResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: List[FunctionBase]
