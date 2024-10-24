from pydantic import BaseModel


class ErrorBaseSchema(BaseModel):
    loc: list[str]
    msg: str
    type: str
