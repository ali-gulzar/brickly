import os
from typing import Union

from fastapi import APIRouter, Depends, File, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from database.model import DBHouse, DBUser
from models.common import Message
from models.user import LoggedInUser, User, UserAttributes, UserDisplay
from models.user_house_association import UserHouseAssociation
from services import (authentication, database, dynamo, rekognition, sns,
                      textract)

router = APIRouter()


OFFLINE = os.environ.get("OFFLINE") == "true"


def verify_user(current_user: DBUser):
    if not current_user.cnic_number_verified or not current_user.phone_number_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{current_user.name} has not verified phone number or cnic number to continue to invest in the lands!",
        )


def verify_investment(house: DBHouse, investment: int):
    if investment > house.value - house.funded:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Investment of {investment} not allowed. Available value of property to invest is {house.value - house.funded}.",
        )


@router.post("/create", response_model=Union[UserDisplay, Message])
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


@router.post("/generate/otp", status_code=status.HTTP_202_ACCEPTED)
def generate_otp(current_user: DBUser = Depends(authentication.get_current_user)):
    phone_number: str = current_user.phone_number
    otp = sns.generate_otp(current_user.name, phone_number)

    if OFFLINE:
        return otp


@router.post("/verify/otp/{otp}", response_model=bool)
def verify_otp(
    otp: str,
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(authentication.get_current_user),
):
    verified = dynamo.verify_otp(current_user.phone_number, otp)
    if verified:
        database.update_user_info(
            current_user.phone_number, UserAttributes.phone_number_verified, True, db
        )
        return True
    return False


@router.post("/verify/cnic", response_model=bool)
def verify_cnic(
    selfie: bytes = File(),
    cnic: bytes = File(),
    current_user: DBUser = Depends(authentication.get_current_user),
    db: Session = Depends(database.get_db),
):
    # get information from id
    id_number_verified = textract.analyze_id(cnic, current_user)
    if not id_number_verified:
        raise HTTPException(
            status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            detail=f"ID card does not match with the information you provided when creating your account. Please check your details or upload a valid CNIC picture!",
        )

    # compare face in id and selfie
    face_verified = rekognition.compare_face(cnic, selfie)
    if not face_verified:
        raise HTTPException(
            status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            detail=f"Face mismatched with the user in CNIC and picture!",
        )

    if id_number_verified and face_verified:
        database.update_user_info(
            current_user.phone_number, UserAttributes.cnic_number_verified, True, db
        )
        return True
    return False


# TODO: store house information in qldb and process the payment
@router.post("/invest/{house_id}", status_code=status.HTTP_202_ACCEPTED)
def invest(
    house_id: str,
    invested_amount: int,
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(authentication.get_current_user),
):
    verify_user(current_user)

    house = database.db_get_house_by_id(house_id, db)
    verify_investment(house, invested_amount)

    database.db_invest(house, current_user, invested_amount, db)
