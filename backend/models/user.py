from pydantic import BaseModel, constr
from typing import Optional

class User(BaseModel):
    phone_number: constr(max_length=11, min_length=11, regex="^[0-9]*$")
    phone_number_verified: Optional[bool] = False
    name: str
    cnic_number: Optional[constr(max_length=13, min_length=13, regex="^[0-9]*$")]
    cnic_number_verified: Optional[bool] = False
    password: str


class UserDisplay(BaseModel):
    phone_number: str
    phone_number_verified: bool
    name: str
    cnic_number: str
    cnic_number_verified: bool

    class Config():
        orm_mode = True


class LoggedInUser(UserDisplay):
    access_token: str
    token_type: str