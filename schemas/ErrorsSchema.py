from typing import List
from pydantic import BaseModel


class ErrorBaseSchema(BaseModel):
    loc: List[str]
    msg: str
    type: str
