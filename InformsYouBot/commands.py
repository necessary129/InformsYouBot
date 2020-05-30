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
from functools import wraps
from . import database as db
from .reddit import user_exists, subreddit_exists
from sqlalchemy.exc import IntegrityError
from . import constants as c
from .template import get_template
from .utils import message_url

from sqlalchemy.orm import joinedload

_COMMANDS = {}
_INV_MSG = r"""Invalid arguments specified for {cmd}.

Required arguments: {args}
"""
_SUB_EXISTS_MSG = r"""You are already subscribed to /u/{author} on /r/{subreddit}
"""
_SUB_NOT_EXISTS_MSG = r"""You are not already subscribed to /u/{author} on /r/{subreddit}
"""
_SUB_REMOVED_MSG = r"""You are now unsubscribed to /u/{author} on /r/{subreddit}
"""


def command(command, *fargs, owner_only=False):
    def wrapper(func):
        _COMMANDS[command] = (func, fargs, owner_only)
        return func

    return wrapper


def check_command(message):
    body = message.body.strip()
    args = body.split()
    command = args.pop(0).lower()[1:]
    if command not in _COMMANDS.keys():
        return
    func, rargs, owner_only = _COMMANDS[command]
    if owner_only:
        user = message.author.name.lower()
        if not user == c.OWNER_USERNAME:
            return
    if len(args) != len(rargs):
        message.reply(
            get_template("base.j2").render(
                message=_INV_MSG.format(cmd=command, args=", ".join(rargs))
            )
        )
        return
    func(message, *args)


@command("post", "Subreddit", owner_only=True)
def post(message, sub):
    sub_s = sub.split("/")[-1].lower()
    subreddit = db.session.query(db.Subreddit).filter_by(name=sub_s).first()
    if not subreddit:
        message.reply(f"The subreddit /r/{sub_s} is not in my database.")
        return
    subreddit.post = True
    db.session.add(subreddit)
    db.session.commit()
    message.reply(f"I will now comment on posts in /r/{sub_s}")


@command("nopost", "Subreddit", owner_only=True)
def nopost(message, sub):
    sub_s = sub.split("/")[-1].lower()
    subreddit = db.session.query(db.Subreddit).filter_by(name=sub_s).first()
    if not subreddit:
        message.reply(f"The subreddit /r/{sub_s} is not in my database.")
        return
    subreddit.post = False
    db.session.add(subreddit)
    db.session.commit()
    message.reply(f"I will not comment on posts in /r/{sub_s} from now on.")


@command("unsubscribe", "Author", "Subreddit")
def unsubscribe(message, auth, sub):
    auth_s = auth.split("/")[-1]
    author_s = auth_s.lower()
    sub_s = sub.split("/")[-1]
    subreddit_s = sub_s.lower()
    subscriber_s = message.author.name.lower()
    subscription = db.get_subscription(subscriber_s, author_s, subreddit_s)
    if not subscription:
        message.reply(
            get_template("base.j2").render(
                message=_SUB_NOT_EXISTS_MSG.format(author=auth_s, subreddit=sub_s)
            )
        )
        return
    try:
        db.session.delete(subscription)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    message.reply(
        get_template("base.j2").render(
            message=_SUB_REMOVED_MSG.format(author=auth_s, subreddit=sub_s)
        )
    )


@command("mysubscriptions")
def mysubscriptions(message):
    subscriber = message.author.name.lower()
    subscriptions = (
        db.session.query(db.Subscription)
        .join(db.Subscription.subscriber)
        .filter(db.User.username == subscriber)
        .options(
            joinedload(db.Subscription.author), joinedload(db.Subscription.subreddit)
        )
        .all()
    )
    message.reply(get_template("subscriptions.j2").render(subscriptions=subscriptions))


@command("subscribe", "Author", "Subreddit")
def subscribe(message, auth, sub):
    auth_s = auth.split("/")[-1]
    author_s = auth_s.lower()
    sub_s = sub.split("/")[-1]
    subreddit_s = sub_s.lower()
    subscriber_s = message.author.name.lower()
    author = db.session.query(db.User).filter_by(username=author_s).first()
    if not author:
        if user_exists(author_s):
            author = db.User(username=author_s)
            try:
                db.session.add(author)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                author = db.session.query(db.User).filter_by(username=author_s).first()
        else:
            message.reply(
                get_template("base.j2").render(
                    message=f"The user /u/{author_s} doesn't exist"
                )
            )
            return
    subreddit = db.session.query(db.Subreddit).filter_by(name=subreddit_s).first()
    if not subreddit:
        if subreddit_exists(subreddit_s):
            subreddit = db.Subreddit(name=subreddit_s)
            try:
                db.session.add(subreddit)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                subreddit = (
                    db.session.query(db.Subreddit).filter_by(name=subreddit_s).first()
                )
        else:
            message.reply(
                get_template("base.j2").render(
                    message=f"The subreddit /r/{subreddit_s} doesn't exist"
                )
            )
            return
    subscriber = db.session.query(db.User).filter_by(username=subscriber_s).first()
    if not subscriber:
        subscriber = db.User(username=subscriber_s)
        db.session.add(subscriber)
        try:
            db.session.add(subscriber)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            subscriber = (
                db.session.query(db.User).filter_by(username=subscriber_s).first()
            )
    subscription = db.Subscription(
        author=author, subreddit=subreddit, subscriber=subscriber
    )
    try:
        db.session.add(subscription)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        message.reply(
            get_template("base.j2").render(
                message=_SUB_EXISTS_MSG.format(author=auth_s, subreddit=sub_s)
            )
        )
        return
    message.reply(
        get_template("base.j2").render(
            message=c.SUBSCRIPTION_SUCCESS.format(author=auth_s, subreddit=sub_s)
        )
    )
