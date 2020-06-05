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
import platform

if platform.python_implementation() == "PyPy":
    try:
        from psycopg2cffi import compat

        compat.register()
    except ImportError:
        pass
import yaml
import random
from itertools import cycle
from functools import wraps
import redis
from urllib.parse import quote

REDIS_CLIENT = redis.Redis()


def only_one(function=None, key=None, timeout=None, block=False):
    """Enforce only one celery task at a time."""

    def _dec(run_func):
        """Decorator."""
        mkey = key if key else run_func.__name__

        @wraps(run_func)
        def _caller(*args, **kwargs):
            """Caller."""
            ret_value = None
            have_lock = False
            lock = REDIS_CLIENT.lock(mkey, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=block)
                if have_lock:
                    ret_value = run_func(*args, **kwargs)
            finally:
                if have_lock:
                    lock.release()

            return ret_value

        return _caller

    return _dec(function) if function is not None else _dec


from praw import Reddit


CONFIG = {}
INSTANCES = []
MAIN_INSTANCE = None


def _load_config():
    global CONFIG
    with open("settings.yaml", mode="r") as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)


def _create_instance_getter():
    global INSTANCE_CYCLE
    INSTANCE_CYCLE = cycle(INSTANCES)


def _load_instances():
    global CONFIG, INSTANCES, MAIN_INSTANCE
    cid = CONFIG["reddit_client_id"]
    csecret = CONFIG["reddit_client_secret"]
    ua = CONFIG["reddit_ua"]
    for account in CONFIG["reddit_accounts"]:
        INSTANCES.append(
            Reddit(
                client_id=cid,
                client_secret=csecret,
                user_agent=ua,
                username=account["username"],
                password=account["password"],
            )
        )
    MAIN_INSTANCE = INSTANCES[0]
    random.shuffle(INSTANCES)
    _create_instance_getter()


def get_main_instance():
    global MAIN_INSTANCE
    return MAIN_INSTANCE


def get_an_instance():
    global INSTANCE_CYCLE
    return next(INSTANCE_CYCLE)


def message_url(recipient, subject, message):
    return "".join(
        (
            "https://np.reddit.com/message/compose/?to=",
            quote(recipient),
            "&subject=",
            quote(subject),
            "&message=",
            quote(message),
        )
    )


_load_config()
_load_instances()
