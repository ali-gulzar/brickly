from enum import Enum

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Roles(str, Enum):
    user = "user"
    estate_agent = "estate_agent"
