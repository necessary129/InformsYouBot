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
