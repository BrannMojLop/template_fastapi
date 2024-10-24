from sqlalchemy import Column, Integer, String, Boolean
from config.Database import BaseModel


class Function(BaseModel):
    __tablename__ = "function"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    is_assigned = Column(Boolean, nullable=False, default=False)
