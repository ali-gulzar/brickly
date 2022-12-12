from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from typing import Union

from services.database import get_db, db_create_user, db_invest, db_get_house_by_id, Hash
from services.authentication import create_access_token, get_current_user
from services.sns import generate_otp
from services.dynamo import verify_otp
from models.user import User, UserDisplay, LoggedInUser
from models.database import DBUser
from models.common import ErrorMessage, Roles

router = APIRouter()

@router.post("/create", response_model=Union[UserDisplay, ErrorMessage])
def create_user(user: User, db: Session = Depends(get_db)):
    return db_create_user(user, db)


@router.post("/login", response_model=LoggedInUser)
def login_user(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user: DBUser = db.query(DBUser).filter(DBUser.phone_number == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with phone number {request.username} does not exist")
    if not Hash.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password!")
    
    access_token = create_access_token(data={'phone_number': user.phone_number, 'name': user.name, 'role': Roles.user})

    return LoggedInUser(phone_number=user.phone_number,
                        phone_number_verified=user.phone_number_verified,
                        name=user.name,
                        cnic_number=user.cnic_number,
                        cnic_number_verified=user.cnic_number_verified,
                        access_token=access_token,
                        token_type='bearer')


@router.post("/generate/phone_number_otp/{phone_number}")
def generate_phone_number_otp(phone_number: str, current_user: DBUser = Depends(get_current_user)):
    return generate_otp(phone_number)


@router.post("/verify/phone_number_otp/{otp}")
def verify_phone_number_otp(otp: str, current_user: DBUser = Depends(get_current_user)):
    return verify_otp('+358449601385', otp)


@router.post("/invest/{house_id}")
def invest(house_id: str, invested_amount: str, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    house = db_get_house_by_id(house_id, db)
    db_invest(house, current_user, db)
    return "Invested successfully!"

