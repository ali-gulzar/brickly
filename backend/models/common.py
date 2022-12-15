from enum import Enum

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Roles(str, Enum):
    user = "user"
    user_description = "Investor in the lands."
    estate_agent = "estate_agent"
    estate_agent_description = (
        "Real estate agent who can add, remove and update lands in the system."
    )


class TextractAPIResponse(str, Enum):
    document_number = "DOCUMENT_NUMBER"
