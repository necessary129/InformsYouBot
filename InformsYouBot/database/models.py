#  Copyright (C) 2020 Shamil K Muhammed

# This file is part of InformsYouBot.

# InformsYouBot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    InformsYouBot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with InformsYouBot.  If not, see <http://www.gnu.org/licenses/>.
from sqlalchemy import (
    MetaData,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from . import engine, session

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        #        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__


Base = declarative_base(bind=engine, metadata=meta, cls=Base)


class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Subreddit(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    post = Column(Boolean, nullable=False, unique=False, default=False)
    last_check = Column(DateTime, nullable=True, unique=False)

    def __repr__(self):
        return f"<Subreddit {self.name}>"


class Subscription(Base):
    __table_args__ = (UniqueConstraint("subreddit_id", "subscriber_id", "author_id"),)
    id = Column(Integer, primary_key=True)
    subreddit_id = Column(
        Integer, ForeignKey("Subreddit.id"), nullable=False, unique=False
    )
    subscriber_id = Column(Integer, ForeignKey("User.id"), nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("User.id"), nullable=False, unique=False)
    subscriber = relationship(
        "User", backref="subscriptions", foreign_keys=[subscriber_id]
    )
    author = relationship("User", backref="subscribed", foreign_keys=[author_id])
    subreddit = relationship("Subreddit", backref="subscriptions")

    def __repr__(self):
        return f"<Subscription {self.id}>"


class KVStore(Base):
    key = Column(String(15), primary_key=True)
    value = Column(String)
