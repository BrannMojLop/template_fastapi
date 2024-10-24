from sqlalchemy import Column, Integer, ForeignKey
from config.Database import BaseModel
from models.auth.App import App
from models.auth.User import User
from models.auth.View import View


class AppViewUser(BaseModel):
    __tablename__ = "app_view_user"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)
    app_id = Column(Integer, ForeignKey(App.id), nullable=True)
    view_id = Column(Integer, ForeignKey(View.id), nullable=False)
