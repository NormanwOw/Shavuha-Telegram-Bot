from sqlalchemy import Integer, String, Column, Boolean
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    full_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    date = Column(String, nullable=False)


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    order_list = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    order_user_time = Column(String, nullable=False)
    order_time = Column(String, nullable=False)
    comment = Column(String, nullable=False)


class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True)
    product = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    desc = Column(String, nullable=False)
    url = Column(String, nullable=False)


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
    mail = Column(Integer, nullable=False)
    selected = Column(Boolean, nullable=False)


class Temp(Base):
    __tablename__ = 'temp'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    product = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)


class Archive(Base):
    __tablename__ = 'archive'

    id = Column(Integer, primary_key=True)
    order_number = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    order_list = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)