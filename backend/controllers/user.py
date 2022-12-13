from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from models.common import ErrorMessage, Roles
from models.database import DBUser
from models.user import LoggedInUser, User, UserDisplay
from services import authentication, database, dynamo, sns

router = APIRouter()


@router.post("/create", response_model=Union[UserDisplay, ErrorMessage])
def create_user(user: User, db: Session = Depends(database.get_db)):
    return database.db_create_user(user, db)


@router.post("/login", response_model=LoggedInUser)
def login_user(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user: DBUser = (
        db.query(DBUser).filter(DBUser.phone_number == request.username).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with phone number {request.username} does not exist",
        )
    if not database.Hash.verify(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password!"
        )

    access_token = authentication.create_access_token(
        data={"phone_number": user.phone_number, "name": user.name}
    )

    return LoggedInUser(
        phone_number=user.phone_number,
        phone_number_verified=user.phone_number_verified,
        name=user.name,
        cnic_number=user.cnic_number,
        cnic_number_verified=user.cnic_number_verified,
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/generate/otp")
def generate_otp(current_user: DBUser = Depends(authentication.get_current_user)):
    phone_number: str = current_user.phone_number
    return sns.generate_otp(phone_number)


@router.post("/verify/otp/{otp}")
def verify_otp(
    otp: str, current_user: DBUser = Depends(authentication.get_current_user)
):
    phone_number = current_user.phone_number
    return dynamo.verify_otp(phone_number, otp)


@router.post("/invest/{house_id}")
def invest(
    house_id: str,
    invested_amount: int,
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(authentication.get_current_user),
):
    house = database.db_get_house_by_id(house_id, db)
    database.db_invest(invested_amount, house, current_user, db)
    return "Invested successfully!"
