from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from unique_names_generator import get_random_name

from database.model import DBUser
from models.common import Roles
from models.house import House, HouseDisplay
from models.user_house_association import UserHouseAssociation
from services import authentication, database

router = APIRouter()


def verify_user(current_user: DBUser, required_role: Roles):
    if not current_user.cnic_number_verified or not current_user.phone_number_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has not authenticated CNIC or phone number!",
        )
    if current_user.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have enough priviliges!",
        )


def verify_sale(user_house: UserHouseAssociation, sale_amount: int):
    if sale_amount > user_house.invested_amount:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Cannot sale land worth of {sale_amount}. You only own {user_house.invested_amount} to sale.",
        )


@router.post("/add", response_model=HouseDisplay)
def add_house(
    house: House,
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(authentication.get_current_user),
):
    verify_user(current_user, Roles.estate_agent)
    if house.name is None:
        house.name = get_random_name()
    return database.db_add_house(house, db)


@router.get("/all", response_model=List[HouseDisplay])
def get_all_houses(db: Session = Depends(database.get_db)):
    return database.db_get_all_houses(db)


@router.patch("/sale/approve/{sale_id}")
def approve_sale(
    sale_id: int,
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(authentication.get_current_user),
):
    pass


@router.patch("/sale/decline/{sale_id}")
def decline_sale(
    sale_id: int,
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(authentication.get_current_user),
):
    pass


@router.post("/sale/{house_id}")
def sale(
    house_id: str,
    sale_amount: int,
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(authentication.get_current_user),
):
    verify_user(current_user, Roles.user)

    user_house: UserHouseAssociation = database.get_user_house(
        house_id, current_user.id, db
    )
    verify_sale(user_house, sale_amount)
