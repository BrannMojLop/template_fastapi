import enum
from sqlalchemy import (
    DateTime,
    Column,
    ForeignKey,
    Integer,
    String,
    func,
    Boolean,
    Enum,
)
from config.Database import BaseModel
from models.UserGroup import UserGroup


class TypeUser(enum.Enum):
    root = "root"


class User(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, nullable=True)
    name = Column(String(255), nullable=False)
    last_name_first = Column(String(255), nullable=False)
    last_name_second = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(10), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    password_temp = Column(String(512), nullable=True)
    password_version = Column(Integer, nullable=False, default=1)
    register_date = Column(DateTime, nullable=False, default=func.now())
    last_login = Column(DateTime, nullable=False, default=func.now())
    is_active = Column(Boolean, nullable=False, default=True)
    type = Column(Enum(TypeUser), nullable=False)
    user_group = Column(Integer, ForeignKey(UserGroup.id), nullable=True)
