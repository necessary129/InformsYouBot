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
from praw.models import Message
from sqlalchemy.orm import contains_eager

from .utils import get_main_instance, get_an_instance, only_one, message_url, CONFIG
from .reddit import get_submissions_newer_than
from . import database as db
from . import constants as c
from .template import get_template


from .commands import check_command


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        10, get_new_submissions.s(), name="Check for new submissions every 30s"
    )
    sender.add_periodic_task(
        11, get_new_messages.s(), name="Check for new messages every 30s"
    )


@app.task
@only_one(timeout=60)
def get_new_messages():
    reddit = get_main_instance()
    messages = []
    non_messages = []
    for item in reddit.inbox.unread():
        if isinstance(item, Message):
            messages.append(item)
        else:
            non_messages.append(item)
    group(process_message.s(m) for m in messages).delay()
    reddit.inbox.mark_read(non_messages)
    reddit.inbox.mark_read(messages)


@app.task
def process_message(message):
    body = message.body.strip().lower()
    if not body.startswith(c.TRIGGER):
        message.mark_read()
        return
    check_command(message)


@app.task
@only_one(timeout=60)
def get_new_submissions():
    subreddits = [s[0] for s in db.session.query(db.Subreddit.name).all()]
    if not subreddits:
        return
    sid = db.session.query(db.KVStore).get("last_sid")
    if not sid:
        sid = db.KVStore(key="last_sid", value="")
    new_subs = get_submissions_newer_than(subreddits, sid.value)
    if not new_subs:
        return
    new_sid = new_subs[0].id
    sid.value = new_sid
    db.session.add(sid)
    db.session.commit()
    group(process_submission.s(sub) for sub in new_subs).delay()


@app.task
def process_submission(submission):
    author = submission.author.name
    subreddit = submission.subreddit.display_name
    subscribers = [
        s.subscriber.username for s in db.get_subscriptions(author, subreddit)
    ]
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
                        f"!unsubscribe /u/{author} /r/{subreddit}",
                    ),
                ),
            ),
        )
    )
    group(
        inform_subscriber.s(subscriber, submission) for subscriber in subscribers
    ).delay()


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
