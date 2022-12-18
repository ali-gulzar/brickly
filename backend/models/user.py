from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, constr

from models.common import Roles


class User(BaseModel):
    phone_number: constr(max_length=11, min_length=11, regex="^[0-9]*$")
    name: str
    cnic_number: Optional[constr(max_length=13, min_length=13, regex="^[0-9]*$")]
    password: str
    role: Roles = Roles.user


class UserDisplay(BaseModel):
    id: int
    phone_number: str
    phone_number_verified: bool
    name: str
    cnic_number: str
    cnic_number_verified: bool
    blocked: bool
    role: Roles
    invested_in: List[dict]

    class Config:
        orm_mode = True


class UserAttributes(str, Enum):
    phone_number_verified = "phone_number_verified"
    cnic_number_verified = "cnic_number_verified"


class LoggedInUser(BaseModel):
    phone_number: str
    phone_number_verified: bool
    name: str
    cnic_number: str
    cnic_number_verified: bool
    access_token: str
    token_type: str
