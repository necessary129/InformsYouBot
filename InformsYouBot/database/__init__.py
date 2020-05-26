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

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from ..utils import CONFIG

engine = create_engine(CONFIG["db_url"])
session = scoped_session(sessionmaker(bind=engine))

from .models import *


def get_subscriptions(author, subreddit):
    return (
        session.query(Subscription)
        .join(Subscription.author)
        .filter(User.username == author.lower())
        .join(Subscription.subreddit)
        .filter(Subreddit.name == subreddit.lower())
        .all()
    )


def get_subscription(subscriber, author, subreddit):
    return (
        session.query(Subscription)
        .join(Subscription.subscriber)
        .filter(User.username == subscriber.lower())
        .join(Subscription.subreddit)
        .filter(Subreddit.name == subreddit.lower())
        .join(Subscription.author, aliased=True)
        .filter(User.username == author.lower())
        .first()
    )
