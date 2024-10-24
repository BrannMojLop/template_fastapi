from sqlalchemy import Column, Integer, String, Boolean
from config.Database import BaseModel


class App(BaseModel):
    __tablename__ = "app"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    def get_name(self):
        return self.name
