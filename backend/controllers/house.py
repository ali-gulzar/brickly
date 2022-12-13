from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from unique_names_generator import get_random_name

from models.house import House, HouseDisplay
from services import database

router = APIRouter()

# for estate agent use
@router.post("/add", response_model=HouseDisplay)
def add_house(house: House, db: Session = Depends(database.get_db)):
    if house.name is None:
        house.name = get_random_name()
    return database.db_add_house(house, db)


@router.get("/all", response_model=List[HouseDisplay])
def get_all_houses(db: Session = Depends(database.get_db)):
    return database.db_get_all_houses(db)
