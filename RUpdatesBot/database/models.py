from sqlalchemy import MetaData, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from . import engine

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__

    id = Column(Integer, primary_key=True)


Base = declarative_base(bind=engine, metadata=meta, cls=Base)


class Subscription(Base):
    Subscriber = Column(String)
    Author = Column(String)
    Subreddit = Column(String)
