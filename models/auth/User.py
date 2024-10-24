from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from config.Database import BaseModel
from models.auth.UserGroup import UserGroup


class User(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String(128), nullable=False, unique=True)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    email = Column(String(512), nullable=True, unique=True)
    phone = Column(String(10), nullable=True, unique=True)
    password_hash = Column(String(512), nullable=False)
    password_temp = Column(String(512), nullable=True)
    password_version = Column(Integer, nullable=False, default=1)
    access_version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    user_group = Column(Integer, ForeignKey(UserGroup.id), nullable=True)
