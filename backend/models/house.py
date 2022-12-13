from typing import List, Optional

from pydantic import BaseModel


class House(BaseModel):
    name: Optional[str]
    location: str
    city: str
    value: int
    funded: Optional[int] = 0


class HouseDisplay(House):
    pass

    class Config:
        orm_mode = True
