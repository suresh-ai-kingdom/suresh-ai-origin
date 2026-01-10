from sqlalchemy import Column, String, Integer, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
import os
import time

Base = declarative_base()

def get_engine(db_url=None):
    if not db_url:
        db_path = os.getenv('DATA_DB', None)
        if db_path:
            db_url = f"sqlite:///{db_path}"
        else:
            db_url = "sqlite:///data.db"
    return create_engine(db_url, connect_args={"check_same_thread": False})


def get_session(engine=None):
    if engine is None:
        engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


class Webhook(Base):
    __tablename__ = 'webhooks'
    id = Column(String, primary_key=True)
    event = Column(String, index=True)
    payload = Column(Text)
    received_at = Column(Float)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(String, primary_key=True)
    amount = Column(Integer)
    currency = Column(String)
    receipt = Column(String)
    product = Column(String, index=True)
    status = Column(String, index=True)
    created_at = Column(Float)
    paid_at = Column(Float, nullable=True)
    payments = relationship('Payment', back_populates='order')


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey('orders.id'), index=True)
    payload = Column(Text)
    received_at = Column(Float)
    order = relationship('Order', back_populates='payments')


def init_models(db_url=None):
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    return engine
