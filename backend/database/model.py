from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.schema import ForeignKey

from models.common import Roles
from models.sale import SaleStatus

Base = declarative_base()

CNIC_NUMBER_LEN = 13
PHONE_NUMBER_LEN = 11


class DBUserHouse(Base):
    __tablename__ = "user_house"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    house_id = Column(Integer, ForeignKey("house.id"), nullable=False)
    invested_amount = Column(Integer)


class DBUserSale(Base):
    __tablename__ = "sale"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    house_id = Column(Integer, ForeignKey("house.id"), nullable=False)
    sale_amount = Column(Integer)
    status = Column(String(10), default=SaleStatus.pending)


class DBUser(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(11), unique=True, nullable=False)
    phone_number_verified = Column(Boolean)
    name = Column(String(256), nullable=False)
    cnic_number = Column(String(13), unique=True, nullable=False)
    cnic_number_verified = Column(Boolean)
    password = Column(String(256), nullable=False)
    blocked = Column(Boolean, default=False)
    role = Column(Enum(Roles), default=Roles.user)
    invested_in = relationship(
        "DBHouse", secondary="user_house", back_populates="investors"
    )
    for_sale = relationship(
        "DBHouse", secondary="sale", back_populates="sale_request"
    )

    @validates("cnic_number")
    def validate_cnic_number(self, key, value):
        if not value or len(value) != CNIC_NUMBER_LEN:
            raise ValueError("Not a valid CNIC number!")
        return value

    @validates("phone_number")
    def validate_phone_number(self, key, value):
        if not value or len(value) != PHONE_NUMBER_LEN:
            raise ValueError("Not a valid phone number!")
        return value


class DBHouse(Base):
    __tablename__ = "house"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    location = Column(String(256), nullable=False)
    city = Column(String(256), nullable=False)
    value = Column(Integer, nullable=False)
    funded = Column(Integer, nullable=False)
    investors = relationship(
        "DBUser", secondary="user_house", back_populates="invested_in"
    )
    sale_request = relationship(
        "DBUser", secondary="sale", back_populates=""
    )
