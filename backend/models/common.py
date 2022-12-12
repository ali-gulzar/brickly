from pydantic import BaseModel
from enum import Enum

class ErrorMessage(BaseModel):
    status_code: str
    message: str


class Roles(str, Enum):
    user = 'user'
    admin = 'admin'
    estate_agent = 'estate_agent'