from enum import Enum

from pydantic import BaseModel


class ErrorMessage(BaseModel):
    status_code: str
    message: str


class Roles(str, Enum):
    user = "user"
    user_description = "Investor in the lands."
    estate_agent = "estate_agent"
    estate_agent_description = (
        "Real estate agent who can add, remove and update lands in the system."
    )
