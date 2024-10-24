from pydantic import BaseModel
from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic
from models.auth.View import View

ViewModel = sqlalchemy_to_pydantic(View)


class ViewBase(ViewModel):
    pass


class ViewsResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: list[ViewBase]


class ViewPost(BaseModel):
    name: str
