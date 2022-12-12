from pydantic import BaseModel
from typing import Optional, List

class House(BaseModel):
    name: Optional[str]
    location: str
    city: str
    value: int
    funded: Optional[int] = 0


class HouseDisplay(House):
    pass

    class Config():
        orm_mode = True