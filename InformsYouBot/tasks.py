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
from .celery import app
from celery import group

# from celery.exceptions import Ignore
from praw.models import Message
from praw.exceptions import RedditAPIException
from sqlalchemy.orm import contains_eager
import datetime

from .utils import (
    get_main_instance,
    get_an_instance,
    only_one,
    message_url,
    CONFIG,
)
from .reddit import get_submissions_newer_than, get_id_from_subs
from . import database as db
from . import constants as c
from .template import get_template


from .commands import check_command


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        10, get_new_submissions.s(), name="Check for new submissions every 10s"
    )
    sender.add_periodic_task(
        11, get_new_messages.s(), name="Check for new messages every 11s"
    )


@app.task
@only_one
def get_new_messages():
    reddit = get_main_instance()
    messages = []
    non_messages = []
    for item in reddit.inbox.unread():
        if isinstance(item, Message):
            messages.append(item)
        else:
            non_messages.append(item)
    for msg in messages:
        process_message.s(msg).apply_async()
    reddit.inbox.mark_read(non_messages)
    reddit.inbox.mark_read(messages)


@app.task
def process_message(message):
    if not message.author:
        return
    body = message.body.strip().lower()
    if not body.startswith(c.TRIGGER):
        message.mark_read()
        return
    check_command(message)


@app.task
@only_one
def get_new_submissions():
    subreddits = [s[0] for s in db.session.query(db.Subreddit.name).all()]
    if not subreddits:
        return
    sid = db.session.query(db.KVStore).get("last_sid")
    if not sid:
        sid = db.KVStore(key="last_sid", value="")
    ld = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
    lc = db.session.query(db.KVStore).get("last_checked_t")
    if not lc:
        lc = db.KVStore(
            key="last_checked_t",
            value=str(
                (
                    (
                        datetime.datetime.now(tz=datetime.timezone.utc)
                        - datetime.timedelta(days=9999)
                    ).timestamp()
                )
            ),
        )
    last_checked = datetime.datetime.fromtimestamp(
        float(lc.value), tz=datetime.timezone.utc
    )
    new_subs = get_submissions_newer_than(subreddits, sid.value, last_checked)
    lc.value = str(ld)
    db.session.add(lc)
    db.session.commit()
    if not new_subs:
        return
    new_sid = get_id_from_subs(new_subs)
    if not new_sid:
        return
    sid.value = new_sid
    db.session.add(sid)
    db.session.commit()
    for sub in new_subs:
        process_submission.s(sub).apply_async()


@app.task
def process_submission(submission):
    try:
        if not (submission.author and submission.id):
            return
    except:
        return
    author = submission.author.name
    subreddit = (
        db.session.query(db.Subreddit)
        .filter_by(name=submission.subreddit.display_name.lower())
        .first()
    )
    subscribers = [
        s.subscriber.username for s in db.get_subscriptions(author, subreddit)
    ]
    try:
        if subreddit.post:
            submission.reply(
                get_template("postcomment.j2").render(
                    author=author,
                    subreddit=subreddit,
                    extra=(
                        (
                            "Unsubscribe",
                            message_url(
                                c.USERNAME,
                                "Unsubscribe",
                                f"!unsubscribe /u/{author} /r/{subreddit.name}",
                            ),
                        ),
                    ),
                )
            )
    except RedditAPIException as e:
        for error in e.items:
            if error.error_type == "THREAD_LOCKED":
                break
        else:
            raise e
    for subscriber in subscribers:
        inform_subscriber.s(subscriber, submission).apply_async()


@app.task
def inform_subscriber(subscriber, submission):
    author = submission.author.name
    subreddit = submission.subreddit.display_name
    url = submission.permalink
    reddit = get_an_instance()
    reddit.redditor(subscriber).message(
        subject="Information",
        message=get_template("base.j2").render(
            message=c.UPDATE_MESSAGE.format(
                author=author, subreddit=subreddit, url=url
            ),
            extra=(
                (
                    "Unsubscribe",
                    message_url(
                        c.USERNAME,
                        "Unsubscribe",
                        f"!unsubscribe /u/{author} /r/{subreddit}",
                    ),
                ),
            ),
        ),
    )
