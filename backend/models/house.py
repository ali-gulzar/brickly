from typing import List, Optional

from pydantic import BaseModel

from models.common import Roles


class Investor(BaseModel):
    id: int
    phone_number: str
    phone_number_verified: bool
    name: str
    cnic_number: str
    cnic_number_verified: bool
    blocked: bool
    role: Roles

    class Config:
        orm_mode = True


class House(BaseModel):
    name: Optional[str]
    location: str
    city: str
    value: int
    funded: Optional[int] = 0


class HouseDisplay(House):
    id: int
    investors: List[Investor]

    class Config:
        orm_mode = True
