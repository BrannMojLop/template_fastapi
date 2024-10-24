from sqlalchemy import Column, ForeignKey, Integer
from config.Database import BaseModel
from models.auth.Function import Function
from models.auth.Permission import Permission


class PermissionFunction(BaseModel):
    __tablename__ = "permission_function"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    function_id = Column(Integer, ForeignKey(Function.id), nullable=False)
    permission_id = Column(Integer, ForeignKey(Permission.id), nullable=False)
