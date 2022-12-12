from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from unique_names_generator import get_random_name

from services.database import get_db, db_add_house, db_get_all_houses
from models.house import House, HouseDisplay


router = APIRouter()

# for estate agent use
@router.post("/add", response_model=HouseDisplay)
def add_house(house: House, db: Session = Depends(get_db)):
    if house.name is None:
        house.name = get_random_name()
    return db_add_house(house, db)


@router.get("/all", response_model=List[HouseDisplay])
def get_all_houses(db: Session = Depends(get_db)):
    return db_get_all_houses(db)


