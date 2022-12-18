import os

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import create_engine, engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from database.model import DBHouse, DBUser
from models.common import Message
from models.house import House
from models.user import User
from services import ssm_store

connection_url = engine.url.URL(
    "mysql+pymysql",
    username=os.environ["DB_USER"],
    password=ssm_store.get_parameter("DATABASE_PASSWORD"),
    host=os.environ["DB_HOST"],
    port=3306,
    database=os.environ["DB_NAME"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_engine(connection_url)
DBSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db_session = DBSession()
    try:
        yield db_session
    finally:
        db_session.close()


class Hash:
    def bcrypt(password: str):
        return pwd_context.hash(password)

    def verify(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)


def commit_to_database_handler(data, db: Session):
    try:
        db.add(data)
        db.commit()
        db.refresh(data)

        return data

    except IntegrityError as e:
        error = e.orig.args
        error_message = error[1]

        return Message(message=error_message)


def db_create_user(user: User, db: Session):
    new_user = DBUser(
        phone_number=user.phone_number,
        phone_number_verified=user.phone_number_verified,
        name=user.name,
        cnic_number=user.cnic_number,
        cnic_number_verified=user.cnic_number_verified,
        password=Hash.bcrypt(user.password),
    )
    return commit_to_database_handler(new_user, db)


def db_get_user_by_phone_number(phone_number: str, db: Session) -> DBUser:
    user: DBUser = db.query(DBUser).filter(DBUser.phone_number == phone_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with phone number {phone_number} not found!",
        )
    return user


def update_user_info(phone_number: str, attribute: str, value: str, db: Session):
    db.query(DBUser).filter(DBUser.phone_number == phone_number).update(
        {attribute: value}
    )
    db.commit()


def db_add_house(house: House, db: Session):
    new_house = DBHouse(
        name=house.name,
        location=house.location,
        city=house.city,
        value=house.value,
        funded=0,
    )
    return commit_to_database_handler(new_house, db)


def db_get_all_houses(db: Session):
    houses = db.query(DBHouse).all()
    return houses


def db_get_house_by_id(id: str, db: Session):
    house = db.query(DBHouse).filter(DBHouse.id == id).first()
    return house


def db_invest(invested_amount: int, house: DBHouse, user: DBUser, db: Session):
    house.funded = house.funded + invested_amount
    user.invested_in.append(house)
    db.commit()
