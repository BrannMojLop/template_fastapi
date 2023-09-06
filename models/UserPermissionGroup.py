from sqlalchemy import Column, Integer, ForeignKey
from config.Database import BaseModel
from models.User import User
from models.Permission import Permission
from models.UserGroup import UserGroup


class UserPermissionGroup(BaseModel):
    __tablename__ = "user_permission_group"

    id = Column(Integer, primary_key=True, index=True, nullable=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)
    group_id = Column(Integer, ForeignKey(UserGroup.id), nullable=True)
    permission_id = Column(Integer, ForeignKey(Permission.id), nullable=False)
