from sqlalchemy import Column, Integer, String, Boolean
from config.Database import BaseModel


class UserGroup(BaseModel):
    __tablename__ = "user_group"

    id = Column(Integer, primary_key=True, index=True, nullable=True)
    name = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
