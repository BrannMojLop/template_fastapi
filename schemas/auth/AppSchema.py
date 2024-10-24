from pydantic import BaseModel
from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic
from models.auth.App import App
from schemas.auth.ViewSchema import ViewBase

AppModel = sqlalchemy_to_pydantic(App)


class AppBase(AppModel):
    pass


class AppDetails(BaseModel):
    app: AppBase
    views: list[ViewBase]


class AppsResponse(BaseModel):
    offset: int
    limit: int
    total: int
    data: list[AppBase]


class AppPost(BaseModel):
    name: str
