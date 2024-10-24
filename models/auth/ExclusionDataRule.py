from sqlalchemy import Column, Integer, ForeignKey, String
from config.Database import BaseModel
from models.auth.User import User


class ExclusionDataRule(BaseModel):
    __tablename__ = "exclusion_data_rule"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    table = Column(String(255), nullable=False)
    user = Column(Integer, ForeignKey(User.id), nullable=False)
    value = Column(String(255), nullable=True)
    record = Column(Integer, nullable=True)
    action = Column(Integer, nullable=True)
