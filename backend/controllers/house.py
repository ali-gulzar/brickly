from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from unique_names_generator import get_random_name

from database.model import DBUser
from models.common import Roles
from models.house import House, HouseDisplay
from services import authentication, database

router = APIRouter()


def verify_user(current_user: DBUser):
    if not current_user.cnic_number_verified or not current_user.phone_number_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has not authenticated CNIC or phone number!",
        )
    if current_user.role != Roles.estate_agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have enough roles to add a house!",
        )


@router.post("/add", response_model=HouseDisplay)
def add_house(
    house: House,
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(authentication.get_current_user),
):
    verify_user(current_user)
    if house.name is None:
        house.name = get_random_name()
    return database.db_add_house(house, db)


@router.get("/all", response_model=List[HouseDisplay])
def get_all_houses(db: Session = Depends(database.get_db)):
    return database.db_get_all_houses(db)
