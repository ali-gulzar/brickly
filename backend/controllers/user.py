import os
from typing import Union

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from models.common import Message
from models.database import DBUser
from models.user import LoggedInUser, User, UserAttributes, UserDisplay
from services import authentication, database, dynamo, sns, textract

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


@router.post("/generate/otp", status_code=status.HTTP_200_OK)
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
    phone_number = current_user.phone_number
    verified = dynamo.verify_otp(phone_number, otp)
    if verified:
        database.update_user_info(
            phone_number, UserAttributes.phone_number_verified, True, db
        )
        return True
    return False


@router.post("/verify/cnic", response_model=Message)
def verify_cnic(
    selfie: UploadFile,
    cnic_bytes: bytes = File(),
    current_user=Depends(authentication.get_current_user),
):
    textract.analyze_id(cnic_bytes)
    return Message(message="CNIC verified!")


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
