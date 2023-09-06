from sqlalchemy import Column, Integer, String, Boolean
from config.Database import BaseModel


class Permission(BaseModel):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, index=True, nullable=True)
    name = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
