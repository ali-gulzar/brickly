from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import validates

Base = declarative_base()

CNIC_NUMBER_LEN = 13
PHONE_NUMBER_LEN = 11

class DBUser(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(11), unique=True) # used to register user (username)
    phone_number_verified = Column(Boolean)
    name = Column(String(256))
    cnic_number = Column(String(13), nullable=True)
    cnic_number_verified = Column(Boolean)
    password = Column(String(256))

    @validates('cnic_number')
    def validate_cnic_number(self, key, value):
        if len(value) != CNIC_NUMBER_LEN:
            raise ValueError("Not a valid CNIC number!")
        return value

    @validates('phone_number')
    def validate_phone_number(self, key, value):
        if  len(value) != PHONE_NUMBER_LEN:
            raise ValueError("Not a valid phone number!")
        return value
