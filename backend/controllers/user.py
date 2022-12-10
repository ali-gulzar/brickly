from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from typing import Union

from services.database import get_db, db_create_user
from models.user import User, UserDisplay
from models.common import ErrorMessage

router = APIRouter()

@router.post("", response_model=Union[UserDisplay, ErrorMessage])
def create_user(user: User, db: Session = Depends(get_db)):
    return db_create_user(user, db)
