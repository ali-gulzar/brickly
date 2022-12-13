from enum import Enum

from pydantic import BaseModel


class ErrorMessage(BaseModel):
    status_code: str
    message: str


class Roles(str, Enum):
    user = "user"
    admin = "admin"
    estate_agent = "estate_agent"
