from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from models.database import DBUser
from services.database import db_get_user_by_phone_number, get_db
from services.ssm_store import get_parameter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

O_AUTH_SECRET_KEY = get_parameter("O_AUTH_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> DBUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, O_AUTH_SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("phone_number")
        if phone_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db_get_user_by_phone_number(phone_number, db)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict):
    data_to_encode = data.copy()
    data_to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=30)})

    encoded_jwt = jwt.encode(data_to_encode, O_AUTH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
