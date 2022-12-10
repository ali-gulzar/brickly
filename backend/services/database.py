import os
from sqlalchemy import engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from services.ssm_store import get_parameter

from models.database import Base, DBUser
from models.user import User
from models.common import ErrorMessage




connection_url = engine.url.URL(
    'mysql+pymysql',
    username=os.environ["DB_USER"],
    password=get_parameter('DATABASE_PASSWORD'),
    host=os.environ["DB_HOST"],
    port=3306,
    database=os.environ["DB_NAME"]
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

engine = create_engine(connection_url)
DBSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# serverless function
def update_database(event, context):
    Base.metadata.create_all(engine)

def get_db():
    db_session = DBSession()
    try:
        yield db_session
    finally:
        db_session.close()

class Hash():
    def bcrypt(password: str):
        return pwd_context.hash(password)
    
    def verify(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)


def db_create_user(user: User, db: Session):
    new_user = DBUser(
        phone_number=user.phone_number,
        phone_number_verified=user.phone_number_verified,
        name=user.name,
        cnic_number=user.cnic_number,
        cnic_number_verified=user.cnic_number_verified,
        password=Hash.bcrypt(user.password)
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError as e:
        error = e.orig.args
        error_code = error[0]
        error_message = error[1]
        return ErrorMessage(status_code=error_code, message=error_message)