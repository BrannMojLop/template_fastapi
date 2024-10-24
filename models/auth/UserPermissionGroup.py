from sqlalchemy import Column, Integer, ForeignKey
from config.Database import BaseModel
from models.auth.User import User
from models.auth.Permission import Permission
from models.auth.UserGroup import UserGroup


class UserPermissionGroup(BaseModel):
    __tablename__ = "user_permission_group"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)
    group_id = Column(Integer, ForeignKey(UserGroup.id), nullable=True)
    permission_id = Column(Integer, ForeignKey(Permission.id), nullable=False)
