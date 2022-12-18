from typing import Optional

from pydantic import BaseModel


class UserHouseAssociation(BaseModel):
    id: int
    invested_amount: Optional[int]
    user_id: int
    house_id: int

    class Config:
        orm_mode = True
