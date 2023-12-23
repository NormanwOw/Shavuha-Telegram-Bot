from sqlalchemy import Integer, BigInteger, String, Column, Boolean
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    full_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    date = Column(String, nullable=False)


class Basket(Base):
    __tablename__ = 'baskets'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    order_list = Column(String, nullable=False)
    price = Column(Integer)
    order_user_time = Column(String)
    order_time = Column(String)
    comment = Column(String)


class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True)
    product = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    url = Column(String)


class Url(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)


class Error(Base):
    __tablename__ = 'errors'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    error = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)


class Mail(Base):
    __tablename__ = 'mails'

    id = Column(Integer, primary_key=True)
    mail = Column(String, nullable=False)
    selected = Column(Boolean, nullable=False)


class Archive(Base):
    __tablename__ = 'archive'

    id = Column(Integer, primary_key=True)
    order_number = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    price = Column(Integer, nullable=False)
    order_list = Column(String, nullable=False)
    comment = Column(String)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)


class Temp(Base):
    __tablename__ = 'temp'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    order_list = Column(String, nullable=False)
