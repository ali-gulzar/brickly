import os
from typing import Union

from fastapi import APIRouter, Depends, File, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from models.common import Message
from models.database import DBUser
from models.user import LoggedInUser, User, UserAttributes, UserDisplay
from services import (authentication, database, dynamo, rekognition, sns,
                      textract)

router = APIRouter()


OFFLINE = os.environ.get("OFFLINE") == "true"


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

    # compare face in id and selfie
    face_verified = rekognition.compare_face(cnic, selfie)

    if id_number_verified and face_verified:
        database.update_user_info(
            current_user.phone_number, UserAttributes.cnic_number_verified, True, db
        )
        return True
    return False


@router.post("/invest/{house_id}")
def invest(
    house_id: str,
    invested_amount: int,
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(authentication.get_current_user),
):
    if not current_user.cnic_number_verified or not current_user.phone_number_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{current_user.name} has not verified phone number or cnic number to continue to invest in the lands!",
        )
    house = database.db_get_house_by_id(house_id, db)
    database.db_invest(invested_amount, house, current_user, db)
    return "Invested successfully!"
